#!/usr/bin/env python

import optparse

import wrangler
import wrangler.db.core
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
    job = wrangler.RenderJob(command=opts.command,
                             start=opts.start,
                             end=opts.end,
                             priority=opts.priority,
                             name=opts.name)
    if opts.verbose:
        print("""Adding Job:
Name:     %s
Command:  %s
Start:    %d
End:      %d
Priority: %d""" % (opts.name, opts.command, opts.start, opts.end, opts.priority))
    client.queue_job(job)
    print 'Job was added to queue.'

if __name__ == '__main__':
    main()