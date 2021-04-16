"""
Create data required to test FBtp and FBti.
"""
tp_count = 0
ti_count = 0
feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
                 VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""
fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id) VALUES (%s, %s, %s) """
syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id """


def create_tip(cursor, code, name, organism_id, db_id,  cvterm_id, feature_id, tp_feature_type_name, pub_id):
    """Create tp or ti."""
    global tp_count, ti_count
    if code == 'ti':
        ti_count += 1
        count = ti_count
    else:
        tp_count += 1
        count = tp_count

    uniquename = "FB{}{:07d}".format(code, count)
    cursor.execute(dbxref_sql, (db_id['FlyBase'], uniquename))
    dbxref_id = cursor.fetchone()[0]

    cursor.execute(feat_sql, (dbxref_id, organism_id, name, uniquename, None, None, cvterm_id[tp_feature_type_name]))
    tp_id = cursor.fetchone()[0]
    feature_id[name] = tp_id

    # add synonyms
    cursor.execute(syn_sql, (name, cvterm_id['symbol'], name))
    tp_symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    cursor.execute(fs_sql, (tp_symbol_id, tp_id, pub_id))

    return tp_id


def create_tpti(cursor, feat_sql, syn_sql, fs_sql, organism_id, db_id, cvterm_id, pub_id, feature_id):
    """Create FBtp and FBti data.

    transposable_element_insertion_site  ti
    transgenic_transposable_element      tp
    """
    # P-element ALready added
    # cursor.execute(feat_sql, (None, organism_id['Dmel'], 'P-element', 'FBte:temp_1', None, None, cvterm_id['natural_transposable_element']))

    for item_prefix in ('TP', 'TI'):
        for i in range(5):
            ti_feature_type_name = 'transposable_element_insertion_site'
            tp_feature_type_name = 'transgenic_transposable_element'
            species = 'Dmel'
            if item_prefix == 'TI':
                ti_feature_type_name = 'insertion_site'
                tp_feature_type_name = 'engineered_region'
                species = 'Ssss'
            tp_name = '{}{}{}{}'.format(item_prefix, '{', i+1, '}')
            ti_name = '{}BGG{}'.format(tp_name, i+1)
            print("Adding {} {}".format(tp_name, ti_name))

            # ti first
            create_tip(cursor, 'ti', ti_name, organism_id['Dmel'], db_id, cvterm_id, feature_id, ti_feature_type_name, pub_id)
            # add tp
            create_tip(cursor, 'tp', tp_name, organism_id[species], db_id, cvterm_id, feature_id, tp_feature_type_name, pub_id)
