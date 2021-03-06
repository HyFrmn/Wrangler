import os
import pwd
import time
import thread
import signal
import datetime
import subprocess

from wrangler import *
from wrangler.config import config_cattle
from wrangler.network import WranglerServer
from wrangler.hardware import info
from wrangler.db.session import Session
from wrangler.db.interface import *
from wrangler.lassod.client import LassoClient


class CattleServer(WranglerServer):
    ASLEEP = 0
    AWAKE = 1
    
    def __init__(self):
        self.configure()
        hostname = info.hostname()
        port = self.config.getint('cattle', 'port')
        WranglerServer.__init__(self, hostname, port, 'wrangler.cattle')

    def _setup(self):
        WranglerServer._setup(self)

        self.client = LassoClient()
        self.running_tasks = {}
        self.max_tasks = self.config.getint('cattle', 'max-tasks')

        self._state = self.ASLEEP

        #Setup Handlers
        self._handles.append(self._handle_metrics)
        self._handles.append(self._handle_pulse)
        #self._handles.append(self._handle_monitor)

        #Setup Timeouts
        self._register_timeout('metrics', self.config.getfloat('cattle', 'metric-frequency'))
        self._register_timeout('task-request', self.config.getfloat('cattle', 'idle'))
        self._register_timeout('pulse', 15.0)
        self._no_tasks = False

        #Thread Locks
        self.num_thread_lock = thread.allocate_lock()

        #Register XMLRPC calls
        self.server.register_function(self.monitor_connect, 'monitor_connect')
        self.server.register_function(self.monitor_disconnect, 'monitor_disconnect')
        self.server.register_function(self.monitor_probe, 'monitor_probe')
        self.server.register_function(self.monitor_start, 'monitor_start')
        self.server.register_function(self.kill_task, 'kill_task')
        self.server.register_function(self.sleep, 'sleep')
        self.server.register_function(self.wake, 'wake')
        self.server.register_function(self.task_list, 'task_list')
        self.server.register_function(self.state, 'state')

        #Connect to lasso.
        self.cattle = connect_cattle(self.hostname)
        self.wake()

    def configure(self):
        self.config = config_cattle()

    def full(self):
        self.num_thread_lock.acquire()
        v = bool(len(self.running_tasks) >= self.max_tasks)
        self.num_thread_lock.release()
        return v

    def shutdown(self):
        WranglerServer.shutdown(self)
        disconnect_cattle(self.hostname)

    def sleep(self):
        self.info("Cattle is going to sleep.")
        if self._state == self.AWAKE:
            self._state = self.ASLEEP
            sleep_cattle(self.hostname)
        return self._state

    def wake(self):
        self.info("Cattle is waking up.")
        if self._state == self.ASLEEP:
            self._state = self.AWAKE
            wake_cattle(self.hostname)
        return self._state

    def task_list(self):
        return map(str, self.running_tasks.keys())

    def state(self):
        return self._state

    def request_task(self):
        self.debug('Requesting task from server.')
        taskid = self.client.next_task(self.hostname)
        if taskid > 0:
            self.info('Task %d was received from server.' % taskid)
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
            self.debug('No task was received from server.')
            self._no_tasks = True

    def monitor_connect(self, task_id):
        self.debug('Monitor for task %d has connected.' % task_id)
        db = Session()
        task = self.running_tasks[task_id]
        db.add(task)
        db.add(task.log)
        task_data = {}
        task_data['command'] = task.run_command
        tries = 0
        while tries < 3:
            try:
                task_data['gid'] = pwd.getpwnam(task.job.owner)[3]
                task_data['uid'] = pwd.getpwnam(task.job.owner)[2]
                break
            except KeyError:
                tries += 1
        task_data['stdout_file_path'] = task.log._stdout_file_path()
        task_data['stderr_file_path'] = task.log._stderr_file_path()
        db.close()
        return task_data

    def monitor_start(self, task_id, pid):
        self.debug('Task %d started process %d' % (task_id, pid))
        self.num_thread_lock.acquire()
        task = self.running_tasks[task_id]
        task.pid = pid
        self.num_thread_lock.release()
        return pid

    def monitor_probe(self, task_id, probes):
        self.debug("Logging probe for %d" % task_id)
        task = self.running_tasks[task_id]
        db = Session()
        probe = TaskProbe()
        db.add(probe)
        cattle = self.cattle
        probe.task_id = task_id
        probe.memory = probes['memory']
        probe.pcpu = probes['pcpu']
        probe.pid = probes['pid']
        #probe.cattle_id = task.log.cattle_id
        probe.time = datetime.datetime.now()
        probe.probes = probes
        probe.cattle_id = cattle.id
        probe.task_log_id = task.log.id
        db.commit()
        probe_id = probe.id
        db.expunge(probe)
        db.close()
        return probe_id

    def kill_task(self, task_id):
        try:
            task = self.running_tasks[task_id]
        except KeyError:
            return False
        try:
            pid = task.pid
        except AttributeError:
            return False
        try:
            os.kill(pid,signal.SIGTERM)
        except OSError:
            os.kill(pid, signal.SIGKILL)
        return True

    def monitor_disconnect(self, task_id, run_time, return_code):
        self.debug('Monitor for task %d had disconnected.' % task_id)
        self._post_task(self.running_tasks[task_id], run_time, return_code)
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
            metrics['running'] = self.running_tasks.keys()
            update_metrics(info.hostname(), metrics)

    def _handle_main(self):
        if self._state == self.ASLEEP:
            return
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
            update_task_log(task.log, -1, -1)
            return False
        return True

    def _post_task(self, task, run_time, return_code):
        self.debug('Postprocessing task %d' % task.id)
        update_task_log(task.log, return_code, run_time)

    def _clean_up_task(self, task):
        self.debug('Cleaning up task %d' % task.id)
        self.num_thread_lock.acquire()
        del self.running_tasks[task.id]
        self.num_thread_lock.release()