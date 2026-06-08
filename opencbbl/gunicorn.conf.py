import multiprocessing
import os

# Server socket
bind = "127.0.0.1:8000"

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2

# Process naming
proc_name = "opencbbl"

# Server mechanics
daemon = False
pidfile = "/tmp/opencbbl.pid"
user = None
group = None
tmp_upload_dir = None

# Logging
accesslog = "/var/log/opencbbl/access.log"
errorlog = "/var/log/opencbbl/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
reload = False

# SSL (if using HTTPS)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("Starting Gunicorn server...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("Reloading Gunicorn server...")

def when_ready(server):
    """Called just after the server is started."""
    print("Gunicorn server is ready. Listening on %s" % server.address)

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print("Worker spawned (pid: %s)" % worker.pid)

def pre_exec(server):
    """Called just before a new master process is forked."""
    print("Forked child, re-executing.")

def worker_int(worker):
    """Called just after a worker received the INT or QUIT signal."""
    print("Worker received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    print("Worker received SIGABRT signal")
