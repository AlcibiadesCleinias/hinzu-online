import multiprocessing

# bind = '0.0.0.0:5000'

# Load application code before the worker processes are forked.
#
preload_app = True

#   backlog - The number of pending connections. This refers
#       to the number of clients that can be waiting to be
#       served. Exceeding this number results in the client
#       getting an error when attempting to connect. It should
#       only affect servers under significant load.
#
#       Must be a positive integer. Generally set in the 64-2048
#       range.
#
backlog = 2048

#   worker_class
#       https://medium.com/@genchilu/brief-introduction-about-the-types-of-worker-in-gunicorn-and-respective-suitable-scenario-67b0c0e7bd62
#   worker_connections - For the eventlet and gevent worker classes
#       this limits the maximum number of simultaneous clients that
#       a single process can handle.
#
#       A positive integer generally set to around 1000.
#   timeout - If a worker does not notify the master process in this
#       number of seconds it is killed and a new worker is spawned
#       to replace it.
#
#       Generally set to thirty seconds. Only set this noticeably
#       higher if you're sure of the repercussions for sync workers.
#       For the non sync workers it just means that the worker
#       process is still communicating and is not tied to the length
#       of time required to handle a single request.
#
#   keepalive - The number of seconds to wait for the next request
#       on a Keep-Alive HTTP connection.
#
#       A positive integer. Generally set in the 1-5 seconds range.
#
workers = multiprocessing.cpu_count() * 2 + 1  # via gunicorn recommendations
worker_class = 'sync'
worker_connections = 1000
timeout = 125
keepalive = 2

#   spew - Install a trace function that spews every line of Python
#       that is executed when running the server. This is the
#       nuclear option.
#
#       True or False
#
spew = False

#   logfile - The path to a log file to write to.
#       A path string. "-" means log to stdout.
#
#   loglevel - The granularity of log output
#       A string of "debug", "info", "warning", "error", "critical"
#
errorlog = 'logs/gunicorn.errorlog.log'
accesslog = 'logs/gunicorn.accesslog.log'
loglevel = 'debug'

#   reload
#       Restart workers when code changes.
#       This setting is intended for development. It will cause workers
#       to be restarted whenever application code changes.
#
reload = False
