
dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id """
feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, type_id)
               VALUES (%s, %s, %s, %s, %s) RETURNING feature_id"""
fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id, is_current) VALUES (%s, %s, %s, %s) """
syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """

feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id)
             VALUES (%s, %s, %s) RETURNING feature_relationship_id """
frp_sql = """ INSERT INTO feature_relationshipprop (feature_relationship_id, type_id, value, rank) VALUES (%s, %s, %s, %s) """
frpub_sql = """ INSERT INTO feature_relationship_pub (feature_relationship_id, pub_id) VALUES (%s, %s) """

pub_sql = """ INSERT INTO pub (type_id, title, uniquename, pyear, miniref) VALUES (%s, %s, %s, %s, %s) RETURNING pub_id """
fp_sql = """ INSERT INTO feature_pub (feature_id, pub_id) VALUES (%s, %s) """
fprop_sql = """ INSERT INTO featureprop (feature_id, type_id, value, rank) VALUES (%s, %s, %s, %s) RETURNING featureprop_id """
fpp_sql = """ INSERT INTO featureprop_pub (featureprop_id, pub_id) VALUES (%s, %s) """

aberration_count = 0


def create_aberration(cursor, count, aberration_prefix, cvterm_id, org_id, db_id, pub_id, feature_id):
    """Get aberration name.

    Args:
        cursor: <sql connection cursor> connection to testdb
        count: <int> to be added to the end of the aberration prefix
        aberration_prefix: <str> aberration name prefix
        cvterm_id: <dict> cvterm name to id
        org_id: <int> organism id
        db_id: <dict> db name to db id
        pub_id: <int> id of pub
        feature_id: <dict> feature name to id
    Returns:
      name and feature_id of newly created aberration.
    """
    global aberration_count
    aberration_count += 1
    aberration_name = "{}{}".format(aberration_prefix, aberration_count)
    aberration_unique_name = 'FB{}{:07d}'.format('ab', (aberration_count))
    aberration_sgml_name = aberration_name

    # create dbxref,  accession -> uniquename
    cursor.execute(dbxref_sql, (db_id['FlyBase'], aberration_unique_name))
    dbxref_id = cursor.fetchone()[0]
    print("name = {}, dbxef = {}, db = {}".format(aberration_name, dbxref_id, db_id['FlyBase']))

    # create the aberration feature
    cursor.execute(feat_sql, (dbxref_id, org_id, aberration_name, aberration_unique_name, cvterm_id['chromosome_structure_variation']))
    aberration_id = feature_id[aberration_name] = cursor.fetchone()[0]

    for syn_type in ('symbol', 'fullname'):
        if syn_type == 'fullname':
            name = "{}-fullname".format(aberration_name)
            sgml_name = "{}-fullname".format(aberration_sgml_name)
        else:
            name = aberration_name
            sgml_name = aberration_sgml_name
        # add synonym for aberration
        cursor.execute(syn_sql, (name, cvterm_id[syn_type], sgml_name))
        symbol_id = cursor.fetchone()[0]

        # add feature_synonym for aberration
        if pub_id != feature_id['unattributed']:
            cursor.execute(fs_sql, (symbol_id, aberration_id, pub_id, True))
        cursor.execute(fs_sql, (symbol_id, aberration_id, feature_id['unattributed'], True))

    # add feature pub for aberration
    cursor.execute(fp_sql, (aberration_id, pub_id))
    return aberration_name, aberration_id


def add_aberration_data(cursor, cvterm_id, org_id, db_id, pub_id, feature_id):
    prefix = "AB(2R)"
    for i in range(10):
        (aber_name, aber_id) = create_aberration(cursor, i, prefix, cvterm_id, org_id, db_id, pub_id, feature_id)
        feature_id[aber_name] = aber_id
        print("aber name {}, is id {}".format(aber_name, aber_id))

        # add featureprop
        cursor.execute(fprop_sql, (aber_id, cvterm_id['new_order'], "Initial value", 0))
        featureprop_id = cursor.fetchone()[0]
        # feature prop pub
        cursor.execute(fpp_sql, (featureprop_id, pub_id))

        # add feature relationship
        if i:
            cursor.execute(feat_rel_sql, (aber_id, (aber_id - 1), cvterm_id['overlap_inferred']))
            fr_id = cursor.fetchone()[0]
            # fr pub
            cursor.execute(frpub_sql, (fr_id, pub_id))
