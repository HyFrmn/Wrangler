#!/usr/bin/env python

import pickle

from wrangler.network import WranglerClient

class LassoClient(WranglerClient):
    def next_task(self):
        pickle_dump = self.client.next_task()
        return pickle.loads(pickle_dump)

    def queue_job(self, job):
        pickle_dump = pickle.dumps(job)
        self.client.queue_job(pickle_dump)