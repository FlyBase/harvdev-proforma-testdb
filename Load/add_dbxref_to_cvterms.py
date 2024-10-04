def add_dbxref_data_to_cvterms(cursor, cv_cvterm_id, db_id, dbxref_id):

    # NOTE: these may not be correct but can be used to create some for testing.
    # The FBxx may not match the actual production ones
    cv_to_FB = {
        #"FlyBase anatomy CV": "FBbt",
        "FlyBase development CV": "FBdv"
        # "FlyBase miscellaneous CV": "FBcv"
    }
    dbx_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id """
    add_to_cvterm = """ UPDATE cvterm SET dbxref_id = %s where cvterm_id = %s """
    for cv in (cv_to_FB.keys()):
        fb_id = db_id[cv_to_FB[cv]]
        count = 1
        for cvterm in cv_cvterm_id[cv]:

            print("Adding CV %s to type %s" % (cvterm, cv_to_FB[cv]))
            print(cv_cvterm_id[cv][cvterm])
            cursor.execute(dbx_sql, (fb_id, count))
            dbx_id = cursor.fetchone()[0]
            cursor.execute(add_to_cvterm, (dbx_id, cv_cvterm_id[cv][cvterm]))
            count += 1