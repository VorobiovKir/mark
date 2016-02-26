#!/bin/bash
NAME=”mark_buff_proj” # Name of the application
DJANGODIR=/home/user/project/works/mark_buff_proj/project # Django project directory
SOCKFILE=/home/user/project/works/mark_buff_proj/project/gunicorn.sock # we will communicte using this unix socket

USER=user # the user to run as
GROUP=user-11111 # the group to run as
NUM_WORKERS=3 # how many worker processes should Gunicorn spawn

MAX_REQUESTS=1 # reload the application server for each request
DJANGO_SETTINGS_MODULE=project.settings # which settings file should Django use
DJANGO_WSGI_MODULE=project.wsgi # WSGI module name

echo “Starting $NAME as `whoami`”

# Activate the virtual environment
cd $DJANGODIR
source /home/user/.virtualenv/mark_buff/bin/activate

export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn’t exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn

# Programs meant to be run under supervisor should not daemonize themselves (do not use –daemon)
exec /home/user/.virtualenv/mark_buff/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
–name $NAME \
–workers $NUM_WORKERS \
–max-requests $MAX_REQUESTS \
–user=$USER –group=$GROUP \
–bind=0.0.0.0:3000 \
–log-level=error \
–log-file=-
