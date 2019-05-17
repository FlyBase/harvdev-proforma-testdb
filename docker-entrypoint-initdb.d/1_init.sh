#!/bin/bash

echo "Running 1_init.sh"
#dropdb fb_test
set -e

echo "# Creating database fb_test"
createdb fb_test
echo "# Adding schema to fb_test"
psql -d fb_test < schema.sql > /dev/null
echo "# Adding test data to fb_test"
python3 add-test_data.py
