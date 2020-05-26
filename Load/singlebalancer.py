"""
:synopsis: Create single balancer data needed for testing.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>
"""


def add_sb_data(cursor, org_dict, cv_cvterm_id, feature_id, pub_id, db_dbxref_id):
    """Add data for Divs.

    Lets create 10 of these and link then to 10 hh's.
    Name might as well be FM{x}c

    """
    div_sql = """ INSERT INTO feature (uniquename, name, type_id, organism_id)
                  VALUES (%s, %s, %s, %s) RETURNING feature_id """
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml)
                  VALUES (%s, %s, %s) RETURNING synonym_id """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id)
                 VALUES (%s, %s, %s) """

    for i in range(1, 11):
        # Add new div feature
        name = "SINGBAL{}".format(i)
        cursor.execute(div_sql, ('FBba:temp_{}'.format(i), name, cv_cvterm_id['FlyBase miscellaneous CV']['single balancer'], org_dict['Dmel']))
        div_id = cursor.fetchone()[0]
        feature_id[name] = div_id

        # synonym
        cursor.execute(syn_sql, (name, cv_cvterm_id['synonym type']['symbol'], name))
        symbol_id = cursor.fetchone()[0]

        # add feature_synonym
        cursor.execute(fs_sql, (symbol_id, div_id, pub_id))
