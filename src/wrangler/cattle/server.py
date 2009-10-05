import os
import time
import thread
import subprocess

from wrangler import *
from wrangler.db.session import Session
from wrangler.db.interface import *
from wrangler.hardware import info
from wrangler.network import WranglerServer
from wrangler.lasso.client import LassoClient


class CattleServer(WranglerServer):
    def _setup(self):
        WranglerServer._setup(self)

        self.client = LassoClient()
        self.running_tasks = {}
        self.max_tasks = self.config.getint('cattle', 'max-tasks')

        #Setup Handlers
        self._handles.append(self._handle_metrics)

        #Setup Timeouts
        self._register_timeout('metrics', self.config.getfloat('metrics', 'frequency'))
        self._register_timeout('task-request', self.config.getfloat('cattle', 'idle'))
        self._no_tasks = False

        #Thread Locks
        self.num_thread_lock = thread.allocate_lock()

        self.connect_cattle(Cattle().hostname)

    def full(self):
        self.num_thread_lock.acquire()
        v = bool(len(self.running_tasks) >= self.max_tasks)
        self.num_thread_lock.release()
        return v

    def connect_cattle(self, hostname):
        db = Session()
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
            metrics['running'] = len(self.running_tasks)
            update_metrics(info.hostname(), metrics)

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
                self.running_tasks[taskid] = []
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
        self.info('Executing task %d' % task.id)
        task_log = create_task_log(task, self.cattle)
        #returncode, delta_time, stdout, stderr = task.run()
        
        environ = os.environ.copy()
        environ.update(task.env)
        for k, v in environ.copy().iteritems():
            environ[str(k)] = str(v)
        try:
            start_time = time.time()
            proc = subprocess.Popen(task.command,
                                    env=environ,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        except OSError, msg:
            self.error(msg)
            proc = None
            update_task_log(task_log, -1, -1,
                            'WRANGLER ERROR: Task did not start.',
                            'WRANGLER ERROR: Task did not start.')
            self.num_thread_lock.acquire()
            del self.running_tasks[task.id]
            self.num_thread_lock.release()
            return None

        pid = proc.pid
        returncode = proc.wait()
        end_time = time.time()
        delta_time = end_time - start_time
        output = proc.stdout.read()
        error = proc.stderr.read()

        update_task_log(task_log, returncode, delta_time, output, error)
        self.info('Finished task %d.' % task.id)

        #Update Running Task Count
        self.num_thread_lock.acquire()
        del self.running_tasks[task.id]
        self.num_thread_lock.release()
        return None