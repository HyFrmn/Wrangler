#!/usr/bin/env python

import cPickle
import wrangler.db
from wrangler import *

def main():
    db = wrangler.db.Session()
    jobs = db.query(Job).all()
    #for job in jobs:
        #print job.id, job.name
        #for task in job.tasks:
            #print task.command
            #pass

if __name__ == '__main__':
    main()