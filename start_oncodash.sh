#!/bin/bash

set -e

usage="Usage: $0 <backend IP> <frontend URL>"

if [[ -z "$1" ]] ; then
    echo "$usage"
    exit 2
fi

if [[ -z "$2" ]] ; then
    echo "$usage"
    exit 2
fi

backend_ip="$1"
frontend_url="$2"
session="oncodash"

if [[ $(tmux has-session -t $session 2> /dev/null) ]] ; then
    tmux kill-session -t $session
fi

# Start a new tmux session.
tmux new -d -s $session \; split-window -v

# BACKEND
tmux send-keys -t $session.0 "cd backend_neo4j ; uv run gunicorn -w 4 -b $backend_ip:5000 'app:app'" ENTER

# FRONTEND
tmux send-keys -t $session.1 "export ONCODASH_API_URL='$frontend_url' ; export ONCODASH_AIFORIA_BRIDGE_URL='https://cloud.aiforia.com' ; cd frontend ; npm run build ; BROWSER=none npm run start" ENTER

tmux attach-session -t $session

