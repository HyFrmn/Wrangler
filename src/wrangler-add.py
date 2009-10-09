#!/usr/bin/env python

import os
import optparse

from wrangler.lasso.client import LassoClient

def main():
    parser = optparse.OptionParser()
    parser.add_option('-c', '--command',
                      help = 'Command to execute.',
                      default = 'echo "Frame $WRANGLER_PADFRAME on $HOSTNAME at `date`"')
    parser.add_option('-n', '--name',
                      help = 'Name of Render Job.',
                      default = 'No Name')
    parser.add_option('-v', '--verbose',
                      help = 'Print verbose output.',
                      action='store_true',
                      default = False)
    parser.add_option('-s', '--start',
                      help = 'Start frame of render.',
                      default = 1,
                      type=int)
    parser.add_option('-e', '--end',
                      help = 'End frame of render.',
                      default = 1,
                      type=int)
    parser.add_option('-p', '--priority',
                      help = "The job's priority. [0 - 1000]",
                      default = 500,
                      type=int)
    
    client = LassoClient()
    opts, args = parser.parse_args()
    if opts.verbose:
        print 'Creating Job'
    job_data = {}
    job_data['generator'] = 'RenderJob'
    job_data['command'] = opts.command
    job_data['start'] = opts.start
    job_data['end'] = opts.end
    job_data['priority'] = opts.priority
    job_data['owner'] = os.environ['USER']
    job_data['name'] = opts.name
    job_data['env'] = os.environ.copy()
    
    if opts.verbose:
        print("""Adding Job:
Name:     %s
Command:  %s
Start:    %d
End:      %d
Priority: %d""" % (opts.name, opts.command, opts.start, opts.end, opts.priority))
    id = client.queue_job(job_data)
    
    print 'Job [%d] was added to queue.' % id

if __name__ == '__main__':
    main()