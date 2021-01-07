"""
:synopsis: Create Disease Implicated Variation data needed for testing.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>
"""


def add_div_data(cursor, org_dict, cv_cvterm_id, feature_id, pub_id, db_dbxref_id):
    """Add data for Divs.

    Lets create 10 of these and link then to 10 hh's.
    Name might as well be Div:p.Arg{x}Gly

    Add dbxref to HGNC, 2 so we can test bangc and bangd
    Similarly for humanhealth_features and feature props.
    """
    div_sql = """ INSERT INTO feature (uniquename, name, type_id, organism_id)
                  VALUES (%s, %s, %s, %s) RETURNING feature_id """
    f_hh = """ INSERT INTO humanhealth_feature (humanhealth_id, feature_id, pub_id)
               VALUES (%s, %s ,%s) """
    f_dbx = """ INSERT INTO feature_dbxref (feature_id, dbxref_id)
                VALUES (%s, %s) """
    fp_sql = """ INSERT INTO featureprop (feature_id, type_id, rank, value)
                 VALUES (%s, %s, %s, %s) """
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml)
                  VALUES (%s, %s, %s) RETURNING synonym_id """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id)
                 VALUES (%s, %s, %s) """

    for i in range(1, 11):
        # Add new div feature
        name = "DIV:p.Arg{}Gly".format(i)
        cursor.execute(div_sql, (name, name, cv_cvterm_id['FlyBase miscellaneous CV']['disease implicated variant'], org_dict['Dmel']))
        div_id = cursor.fetchone()[0]

        # add 2 humanhealth features for this
        cursor.execute(f_hh, (feature_id['hh-symbol-{}'.format(i)], div_id, pub_id))
        cursor.execute(f_hh, (feature_id['hh-symbol-{}'.format(i+1)], div_id, pub_id))

        # add 2 feature dbxref's
        cursor.execute(f_dbx, (div_id, db_dbxref_id['HGNC']['{}'.format(i)]))
        cursor.execute(f_dbx, (div_id, db_dbxref_id['HGNC']['{}'.format(i+1)]))

        # add 2 featureprop comments
        cursor.execute(fp_sql, (div_id,
                                cv_cvterm_id['FlyBase miscellaneous CV']['comment'],
                                0,
                                'set comment {}'.format(i)))
        cursor.execute(fp_sql, (div_id,
                                cv_cvterm_id['FlyBase miscellaneous CV']['comment'],
                                1,
                                'set comment {}'.format(i+1)))

        # synonym
        cursor.execute(syn_sql, (name, cv_cvterm_id['synonym type']['symbol'], name))
        symbol_id = cursor.fetchone()[0]

        # add feature_synonym
        cursor.execute(fs_sql, (symbol_id, div_id, pub_id))

    # And some funky examples
    for i in range(13, 15):
        # Add new div feature
        name = "C9orf72:n.intron{}[30GGGGCC]".format(i)
        cursor.execute(div_sql, (name, name, cv_cvterm_id['FlyBase miscellaneous CV']['disease implicated variant'], org_dict['Dmel']))
        div_id = cursor.fetchone()[0]

        # add 2 humanhealth features for this
        cursor.execute(f_hh, (feature_id['hh-symbol-{}'.format(i)], div_id, pub_id))
        cursor.execute(f_hh, (feature_id['hh-symbol-{}'.format(i+1)], div_id, pub_id))

        # add 2 feature dbxref's
        cursor.execute(f_dbx, (div_id, db_dbxref_id['HGNC']['{}'.format(i)]))
        cursor.execute(f_dbx, (div_id, db_dbxref_id['HGNC']['{}'.format(i+1)]))

        # add 2 featureprop comments
        cursor.execute(fp_sql, (div_id,
                                cv_cvterm_id['FlyBase miscellaneous CV']['comment'],
                                0,
                                'set comment {}'.format(i)))
        cursor.execute(fp_sql, (div_id,
                                cv_cvterm_id['FlyBase miscellaneous CV']['comment'],
                                1,
                                'set comment {}'.format(i+1)))

        # synonym
        cursor.execute(syn_sql, (name, cv_cvterm_id['synonym type']['symbol'], name))
        symbol_id = cursor.fetchone()[0]

        # add feature_synonym
        cursor.execute(fs_sql, (symbol_id, div_id, pub_id))
