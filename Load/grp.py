grp_sql = """ INSERT INTO grp (name, uniquename, type_id) VALUES (%s, %s, %s) RETURNING grp_id """
grp_syn_sql = """ INSERT INTO grp_synonym (grp_id, synonym_id, pub_id, is_current) VALUES (%s, %s, %s, %s) """
syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
grp_dbxref_sql = """ INSERT INTO grp_dbxref (grp_id, dbxref_id) VALUES (%s, %s) """
grp_cvterm_sql = """ INSERT INTO grp_cvterm (grp_id, cvterm_id, pub_id) VALUES (%s, %s, %s) """
grp_prop_rank_sql = """ INSERT INTO grpprop (grp_id, type_id, value, rank) VALUES (%s, %s, %s, %s) RETURNING grpprop_id """
grp_prop_sql = """ INSERT INTO grpprop (grp_id, type_id, value) VALUES (%s, %s, %s) RETURNING grpprop_id """
grp_proppub_sql = """ INSERT INTO grpprop_pub (grpprop_id, pub_id) VALUES (%s, %s) """
grp_pub_sql = """ INSERT INTO grp_pub (grp_id, pub_id) VALUES (%s, %s) """
grp_relationship_sql = """ INSERT INTO grp_relationship (subject_id, object_id, type_id) VALUES (%s, %s, %s) RETURNING grp_relationship_id"""
grp_relationshippub_sql = """ INSERT INTO grp_relationship_pub (grp_relationship_id, pub_id) VALUES (%s, %s) """


def add_grp_data(cursor, feature_id, cvterm_id, dbxref_id, pub_id):
    """Load gene grp info"""
    for i in range(1, 15):
        # grp
        cursor.execute(grp_sql, ('grp-{}'.format(i), 'FBgg:temp_{}'.format(i), cvterm_id['gene_group']))
        feature_id['grp-{}'.format(i)] = grp_id = cursor.fetchone()[0]

        # grp fullname syn
        cursor.execute(syn_sql, ('grp-fullname-{}'.format(i), cvterm_id['fullname'], 'grp-fullname-{}'.format(i)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(grp_syn_sql, (grp_id, syn_id, pub_id, True))

        # grp symbol syn
        cursor.execute(syn_sql, ('grp-{}'.format(i), cvterm_id['symbol'], 'grp-{}'.format(i)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(grp_syn_sql, (grp_id, syn_id, feature_id['unattributed'], True))
        cursor.execute(grp_syn_sql, (grp_id, syn_id, pub_id, True))

        # add alternative synonyms
        cursor.execute(syn_sql, ('alt-grp-{}'.format(i), cvterm_id['symbol'], 'alt-grp-{}'.format(i)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(grp_syn_sql, (grp_id, syn_id, pub_id, False))
        cursor.execute(syn_sql, ('alt2-grp-{}'.format(i), cvterm_id['symbol'], 'alt2-grp-{}'.format(i)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(grp_syn_sql, (grp_id, syn_id, pub_id, False))

        # add pubs
        cursor.execute(grp_pub_sql, (grp_id, pub_id))
        cursor.execute(grp_pub_sql, (grp_id, feature_id['unattributed']))

        # add dbxref HGNC-GG1 accession 1
        cursor.execute(grp_dbxref_sql, (grp_id, dbxref_id['HGNC-GG1-acc']))

        # add cvterms
        cursor.execute(grp_cvterm_sql, (grp_id, cvterm_id['functional group'], pub_id))
        cursor.execute(grp_cvterm_sql, (grp_id, cvterm_id['something'], pub_id))
        cursor.execute(grp_cvterm_sql, (grp_id, cvterm_id['nucleolus'], pub_id))

        # add prop
        cursor.execute(grp_prop_sql, (grp_id, cvterm_id['gg_owner'], 'owner-{}'.format(i)))
        grpprop_id = cursor.fetchone()[0]
        # add proppub
        cursor.execute(grp_proppub_sql, (grpprop_id, pub_id))

        # add more of one type to test bangd
        cursor.execute(grp_prop_rank_sql, (grp_id, cvterm_id['gg_description'], 'line1', 0))
        grpprop_id = cursor.fetchone()[0]
        cursor.execute(grp_proppub_sql, (grpprop_id, pub_id))

        cursor.execute(grp_prop_rank_sql, (grp_id, cvterm_id['gg_description'], 'line2', 1))
        grpprop_id = cursor.fetchone()[0]
        cursor.execute(grp_proppub_sql, (grpprop_id, pub_id))

        # add parent relationship
        if i > 1:
            cursor.execute(grp_relationship_sql, (grp_id, feature_id['grp-{}'.format(i-1)], cvterm_id['parent_grp']))
            grp_rel_id = cursor.fetchone()[0]
            # now add the pub
            cursor.execute(grp_relationshippub_sql, (grp_rel_id, pub_id))
