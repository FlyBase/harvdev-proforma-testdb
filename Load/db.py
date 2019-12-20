# Create db's for db testing
# Some with urls some without


def add_db_data(cursor, db_id):
    db_sql = """  INSERT INTO db (name) VALUES (%s) RETURNING db_id """
    full_db_sql = """  INSERT INTO db (name, description, url, urlprefix) VALUES (%s, %s, %s, %s) RETURNING db_id """

    for i in range(5):
        name = "Test_full_{}".format(i+1)
        description = "Description for {}".format(name)
        cursor.execute(full_db_sql, (name, description, "https://url.com/test_{}".format(i+1), "https://url.com/test_{}/gene=?".format(i+1)))
        db_id[name] = cursor.fetchone()[0]

    for i in range(5):
        name = "Test_{}".format(i+1)
        cursor.execute(db_sql, (name,))
        db_id[name] = cursor.fetchone()[0]
