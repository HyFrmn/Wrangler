import os
import time
import thread
import subprocess

from wrangler import *
from wrangler.network import WranglerServer
from wrangler.hardware import info
from wrangler.db.session import Session
from wrangler.db.interface import *
from wrangler.lasso.client import LassoClient

class CattleServer(WranglerServer):
    def _setup(self):
        WranglerServer._setup(self)

        self.client = LassoClient()
        self.running_tasks = {}
        self.max_tasks = self.config.getint('cattle', 'max-tasks')

        #Setup Handlers
        self._handles.append(self._handle_metrics)
        self._handles.append(self._handle_pulse)
        self._handles.append(self._handle_monitor)

        #Setup Timeouts
        self._register_timeout('metrics', self.config.getfloat('metrics', 'frequency'))
        self._register_timeout('task-request', self.config.getfloat('cattle', 'idle'))
        self._register_timeout('pulse', 15.0)
        self._no_tasks = False

        #Thread Locks
        self.num_thread_lock = thread.allocate_lock()

        self.cattle = connect_cattle(self.hostname)

    def full(self):
        self.num_thread_lock.acquire()
        v = bool(len(self.running_tasks) >= self.max_tasks)
        self.num_thread_lock.release()
        return v

    def shutdown(self):
        WranglerServer.shutdown(self)
        disconnect_cattle(self.hostname)

    def request_task(self):
        self.debug('Requesting task from server.')
        taskid = self.client.next_task()
        if taskid > 0:
            self.debug('Task %d was recieved from server.' % taskid)
            db = Session()
            task = db.query(Task).filter_by(id=taskid).first()
            db.expunge(task)
            db.close()
            if task:
                self.num_thread_lock.acquire()
                self.running_tasks[taskid] = task
                self.num_thread_lock.release()
                self._pre_task(task)
                if not self._run_task(task):
                    self._clean_up_task(task)
                self._no_tasks = False
        else:
            self.debug('No task was recieved from server.')
            self._no_tasks = True

    def _handle_pulse(self):
        if self._timeout('pulse'):
            self.debug('Pulsing lasso server.')
            self.client.pulse(self.hostname)

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

    def _handle_monitor(self):
        for id, task in self.running_tasks.copy().items():
            if task:
                poll = task.proc.poll()
                if poll is not None:
                    self.debug('Finished task %d' % id)
                    self._post_task(task)
                    self._clean_up_task(task)
                else:
                    if self._timeout('task-id-%d' % task.id):
                        pass

    def _handle_main(self):
        if not self.full():
            if self._no_tasks:
                if self._timeout('task-request'):
                    self.request_task()
            else:
                self.request_task()

    def _pre_task(self, task):
        self.debug('Preprocessing task %d' % task.id)

        # Create final task command.
        task.run_command = task.command
        env = os.environ.copy()
        env.update(task.env)
        for k, v in env.copy().iteritems():
            env[str(k)] = str(v)
        task.run_env = env

        # Create task log.
        task.log = create_task_log(task, self.cattle)

    def _run_task(self, task):
        self.debug('Executing task %d' % task.id)
        #Start Process
        try:
            task.start_time = time.time()
            task.proc = subprocess.Popen(task.run_command,
                                env = task.run_env,
                                shell = True,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE)
        except OSError, msg:
            self.error(msg)
            update_task_log(task.log, -1, -1,
                'WRANGLER ERROR: Task did not start.',
                'WRANGLER ERROR: Task did not start.')
            return False
        self._register_timeout('task-id-%d' % task.id, 5)
        return True

    def _post_task(self, task):
        self.debug('Postprocessing task %d' % task.id)
        end_time = time.time()
        delta_time = end_time - task.start_time
        returncode = task.proc.returncode
        stdout = task.proc.stdout.read()
        stderr = task.proc.stderr.read()
        update_task_log(task.log, returncode, delta_time, stdout, stderr)

    def _clean_up_task(self, task):
        self.debug('Cleaning up task %d' % task.id)
        self.num_thread_lock.acquire()
        del self.running_tasks[task.id]
        self.num_thread_lock.release()