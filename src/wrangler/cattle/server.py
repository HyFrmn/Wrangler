import os
import pwd
import time
import thread
import subprocess

from wrangler import *
from wrangler.config import config_base
from wrangler.network import WranglerServer
from wrangler.hardware import info
from wrangler.db.session import Session
from wrangler.db.interface import *
from wrangler.lasso.client import LassoClient


class CattleServer(WranglerServer):
    def __init__(self):
        hostname = info.hostname()
        config = config_base()
        port = config.getint('cattle', 'port')
        WranglerServer.__init__(self, hostname, port, 'wrangler.cattle')

    def _setup(self):
        WranglerServer._setup(self)

        self.client = LassoClient()
        self.running_tasks = {}
        self.max_tasks = self.config.getint('cattle', 'max-tasks')

        #Setup Handlers
        self._handles.append(self._handle_metrics)
        self._handles.append(self._handle_pulse)
        #self._handles.append(self._handle_monitor)

        #Setup Timeouts
        self._register_timeout('metrics', self.config.getfloat('metrics', 'frequency'))
        self._register_timeout('task-request', self.config.getfloat('cattle', 'idle'))
        self._register_timeout('pulse', 15.0)
        self._no_tasks = False

        #Thread Locks
        self.num_thread_lock = thread.allocate_lock()

        #Register XMLRPC calls
        self.server.register_function(self.monitor_connect, 'monitor_connect')
        self.server.register_function(self.monitor_disconnect, 'monitor_disconnect')

        #Connect to lasso.
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

    def monitor_connect(self, task_id):
        print 'Monitor for task %d has connected.' % task_id
        db = Session()
        task = self.running_tasks[task_id]
        db.add(task)
        db.add(task.log)
        task_data = {}
        task_data['command'] = task.run_command
        task_data['gid'] = pwd.getpwnam(task.job.owner)[3]
        task_data['uid'] = pwd.getpwnam(task.job.owner)[2]
        task_data['stdout_file_path'] = task.log._stdout_file_path()
        task_data['stderr_file_path'] = task.log._stderr_file_path()
        db.close()
        return task_data


    def monitor_disconnect(self, task_id):
        print 'Monitor for task %d had disconnected.' % task_id
        self._post_task(self.running_tasks[task_id])
        self._clean_up_task(self.running_tasks[task_id])
        return task_id

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
        task.owner = task.job.owner
        # Create task log.
        task.log = create_task_log(task, self.cattle)

    def _run_task(self, task):
        self.debug('Executing task %d' % task.id)
        #Start Process
        cattle_monitor_path = os.path.join(os.path.dirname(__file__), 'monitor.py')
        command_call = '%s %d' % (cattle_monitor_path, task.id)
        try:
            task.start_time = time.time()
            task.proc = subprocess.Popen(command_call,
                                env = task.run_env,
                                shell = True)
        except OSError, msg:
            self.error(msg)
            update_task_log(task.log, -1, -1,
                'WRANGLER ERROR: Task did not start.',
                'WRANGLER ERROR: Task did not start.')
            return False
        return True

    def _post_task(self, task):
        self.debug('Postprocessing task %d' % task.id)
        update_task_log(task.log, 0, -1, 'Not Implemented', 'Not Implemented')

    def _clean_up_task(self, task):
        self.debug('Cleaning up task %d' % task.id)
        self.num_thread_lock.acquire()
        del self.running_tasks[task.id]
        self.num_thread_lock.release()