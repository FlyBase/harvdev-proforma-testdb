"""
:synopsis: Create Disease Implicated Variation data needed for testing.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>
"""


def add_div_data(cursor, org_dict, cvterm_id, feature_id, pub_id, db_dbxref_id):
    """Add data for Divs.

    Lets create 10 of these and link then to 10 hh's.
    Name might as well be Div:p.ArgxGly

    Add dbxref to HGNC
    """
    div_sql = """ INSERT INTO feature (uniquename, name, type_id, organism_id)
                  VALUES (%s, %s, %s, %s) RETURNING feature_id """
    f_hh = """ INSERT INTO humanhealth_feature (humanhealth_id, feature_id, pub_id)
               VALUES (%s, %s ,%s) """
    f_dbx = """ INSERT INTO feature_dbxref (feature_id, dbxref_id)
                VALUES (%s, %s) """
    for i in range(1, 11):
        # Add new div feature
        name = "DIV:p.Arg{}Gly".format(i)
        cursor.execute(div_sql, (name, name, cvterm_id['div'], org_dict['Dmel']))
        div_id = cursor.fetchone()[0]

        # add humanhealth feature for this
        cursor.execute(f_hh, (feature_id['hh-symbol-{}'.format(i)], div_id, pub_id))

        # add feature dbxref
        cursor.execute(f_dbx, (div_id, db_dbxref_id['HGNC']['{}'.format(i)]))
