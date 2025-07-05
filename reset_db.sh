#!/bin/bash

# CODEX: Delete the SQLite database and reinitialize schema
set -e

rm -f backend/data.db
python - <<'PY'
import sys
sys.path.insert(0, 'backend')
import database
# CODEX: Recreate SQLite schema
database.init_db()
PY

echo "Database reset to clean state."
