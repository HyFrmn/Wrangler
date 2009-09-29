import time
import thread


from wrangler import *
from wrangler.db.session import Session
from wrangler.db.interface import *
from wrangler.hardware import info
from wrangler.network import WranglerServer
from wrangler.lasso.client import LassoClient


class CattleServer(WranglerServer):
    def _setup(self):
        WranglerServer._setup(self)
        self.running_tasks = 0
        self.total_running_tasks = 2
        self.client = LassoClient()

        #Setup Handlers
        self._handles.append(self._handle_metrics)

        #Setup Timeouts
        self._register_timeout('metrics', self.config.getfloat('metrics', 'frequency'))
        self._register_timeout('task-request', 15)
        self._no_tasks = False

        #Thread Locks
        self.num_thread_lock = thread.allocate_lock()

        self.connect_cattle(Cattle().hostname)

    def full(self):
        self.num_thread_lock.acquire()
        db = Session()
        db.add(self.cattle)
        v = bool(self.cattle.running >= self.total_running_tasks)
        db.commit()
        db.close()
        self.num_thread_lock.release()
        return v

    def connect_cattle(self, hostname):
        db = Session()
        print hostname
        found = db.query(Cattle).filter(Cattle.hostname==hostname).first()
        if found:
            self.debug('Found cattle in database.')
            cattle = found
        else:
            self.debug('No cattle found in database, creating new row.')
            cattle = Cattle()
            db.add(cattle)
        cattle.enabled = True
        self.cattle = cattle
        db.commit()
        self.cattle_id = cattle.id
        db.expunge(cattle)
        db.close()
        self.debug('%s was added to the heard.' % hostname)

    def disconnect_cattle(self):
        db = Session()
        db.add(self.cattle)
        self.cattle.enabled = False
        db.commit()
        db.close()

    def shutdown(self):
        WranglerServer.shutdown(self)
        self.disconnect_cattle()

    def _handle_metrics(self):
        if self._timeout('metrics'):
            self.debug('Logging metrics')
            metrics = {}
            metrics['hostname'] = info.hostname()
            metrics['time'] = time.time()
            metrics['load_avg'] = info.load_avg()
            metrics['memory'] = info.memory()
            metrics['running'] = self.running_tasks
            self.client.update_metrics(info.hostname(), metrics)

    def request_task(self):
        self.debug('Requesting task from server.')
        taskid = self.client.next_task()
        if taskid:
            self.debug('Task %d was recieved from server.' % taskid)
            db = Session()
            task = db.query(Task).filter_by(id=taskid).first()
            db.expunge(task)
            db.close()
            if task:
                self.num_thread_lock.acquire()
                db = Session()
                db.add(self.cattle)
                self.cattle.running += 1
                db.commit()
                db.close()
                self.num_thread_lock.release()
                thread.start_new_thread(self._monitor, (task,))
                self._no_tasks = False
        else:
            self.debug('No task was recieved from server.')
            self._no_tasks = True

    def _handle_main(self):
        if not self.full():
            if self._no_tasks:
                if self._timeout('task-request'):
                    self.request_task()
            else:
                self.request_task()

    def _monitor(self, task):
        self.debug('Executing task %d' % task.id)
        returncode, delta_time, stdout, stderr = task.run()

        #Log task results. 
        db = Session()
        db.add(task)
        task.status = task.FINISHED
        task_log = TaskLog(task, returncode, delta_time, stdout, stderr, self.cattle_id)
        db.add(task_log)
        db.commit()
        self.info('Finished task %d.' % task.id)
        job = task.job
        db.close()

        #Update Task
        self.num_thread_lock.acquire()
        db = Session()
        db.add(self.cattle)
        self.cattle.running -= 1
        db.commit()
        db.close()
        self.num_thread_lock.release()
        update_job(job)
        return None