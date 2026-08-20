#!/bin/bash
set -e

echo "Initializing database..."
python -c "from backend.database.init_db import init_db; init_db()"

echo "Seeding database..."
python -c "from backend.database.seed_data import seed_database; seed_database()"

echo "Database initialization complete!"

