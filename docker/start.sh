#!/bin/bash
set -e
python backend/app.py &
BACK_PID=$!
cd frontend
npx vite preview --host --port 5173 --strictPort &
FRONT_PID=$!
trap "kill $BACK_PID $FRONT_PID" SIGTERM SIGINT
wait -n $BACK_PID $FRONT_PID

