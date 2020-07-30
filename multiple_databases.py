#!/usr/bin/python
import psycopg2
import sys

database_copies = int(sys.argv[1])
source_branch = str(sys.argv[2])

conn = psycopg2.connect(database="template1")
conn.autocommit = True
cursor = conn.cursor()

print('Database copies set to {}. Source branch set to {}.'.format(database_copies, source_branch))

if database_copies > 0 and source_branch != 'master':
    print('Creating {} copies of the test database.'.format(database_copies), flush=True)
    for number in range(0, database_copies):
        cursor.execute("CREATE DATABASE fb_test_{} TEMPLATE fb_test;".format(number))
        print('Copy of fb_test created as fb_test_{}'.format(number), flush=True)
else:
    print('Additional copies of fb_test will not be created.')
    print('To create copies, database_copies (sys.argv[1]) must be >0 '
          'and source_branch (sys.argv[2]) must not be master.')

