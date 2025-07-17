#!/bin/bash
set -e
python backend/app.py &
BACK_PID=$!
cd frontend
npx vite preview --host 0.0.0.0 --port 5173 --strictPort &
FRONT_PID=$!
trap "kill $BACK_PID $FRONT_PID" SIGTERM SIGINT
wait -n $BACK_PID $FRONT_PID

