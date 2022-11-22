def add_seqfeat_data(cursor, cvterm_id, organism_id, dbxref_id, pub_id, db_id, feature_id):
    """Add seqfest data"""
    print("Adding seqfeat data.")

    chemical_sql = """ INSERT INTO feature (name, uniquename, organism_id, type_id, dbxref_id, is_obsolete)
                      VALUES (%s, %s, %s, %s, %s, %s) RETURNING feature_id"""
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id, is_current)
                 VALUES (%s, %s, %s, %s) """
    feat_pub_sql = """ INSERT INTO feature_pub (feature_id, pub_id) VALUEs (%s, %s)"""
    dbxref_sql = """ INSERT INTO dbxref (db_id, accession)
                     VALUES (%s, %s) RETURNING dbxref_id"""
    fd_sql = """ INSERT INTO feature_dbxref (feature_id, dbxref_id)
                 VALUES (%s, %s) """

    featprop_sql = """ INSERT INTO featureprop (feature_id, type_id, rank, value)
                       VALUES (%s, %s, %s, %s) RETURNING featureprop_id"""
    fppub_sql = """ INSERT INTO featureprop_pub (featureprop_id, pub_id) VALUES (%s, %s) """

    feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id)
                       VALUES (%s, %s, %s) RETURNING feature_relationship_id """
    frp_sql = """ INSERT INTO feature_relationshipprop (feature_relationship_id, type_id, value, rank)
                  VALUES (%s, %s, %s, %s) RETURNING  feature_relationshipprop_id"""
    frpub_sql = """ INSERT INTO feature_relationshipprop_pub (feature_relationshipprop_id, pub_id) VALUES (%s, %s) """

    obsolete = False
    for i in range(9):
        cursor.execute(dbxref_sql, (db_id['FlyBase'], 'FBsf000000000{}'.format(i+1)))
        dx_id = cursor.fetchone()[0]
        cursor.execute(chemical_sql, ('seqfeat-{}'.format(i+1), 'FBsf000000000{}'.format(i+1),
                       organism_id['Dmel'], cvterm_id['regulatory_region'], dx_id, obsolete))
        sf_id = cursor.fetchone()[0]

        # feat db_xref
        cursor.execute(fd_sql, (sf_id, dx_id))

        ##########
        # synonyms
        ##########
        cursor.execute(syn_sql, ('seqfeat{}'.format(i+1), cvterm_id['symbol'], 'seqfeat{}'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, sf_id, pub_id, True))

        ####################################
        # seq feat have NO fullname synonyms
        ####################################
        # cursor.execute(syn_sql, ('seqfeat-{}'.format(i+1), cvterm_id['fullname'], 'seqfeat-{}'.format(i+1)))
        # syn_id = cursor.fetchone()[0]
        # cursor.execute(fs_sql, (syn_id, sf_id, pub_id, True))
        # cursor.execute(fs_sql, (syn_id, sf_id, feature_id['unattributed'], True))

        # seqfeature-X [symbol], is_current FALSE
        cursor.execute(syn_sql, ('seqfeature-{}'.format(i+1), cvterm_id['symbol'], 'seqfeature-{}'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, sf_id, pub_id, False))

        # cursor.execute(syn_sql, ('seqfeature-{}'.format(i+1), cvterm_id['fullname'], 'seqfeature-{}'.format(i+1)))
        # syn_id = cursor.fetchone()[0]
        # cursor.execute(fs_sql, (syn_id, sf_id, pub_id, False))

        # Feat pub
        cursor.execute(feat_pub_sql, (sf_id, feature_id['unattributed']))

        ################
        # Add FeatureLoc
        ################
        # NOT sure if you can merge with a feature loc?
        # Lets see...
        # print("\t FeatureLoc to point mutation added to 2L:10..11")
        # cursor.execute(loc_sql, (sf_id, feature_id['2L'], 10, 11, 1))

        ############
        # Add props.
        ############

        # internal notes
        cursor.execute(featprop_sql, (sf_id, cvterm_id['internalnotes'], 0, f"inote_{i+1}_1"))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fppub_sql, (fp_id, pub_id))

        # evidence
        cursor.execute(featprop_sql, (sf_id, cvterm_id['evidence'], 0, f"evidence_{i+1}_1"))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fppub_sql, (fp_id, pub_id))
        cursor.execute(featprop_sql, (sf_id, cvterm_id['evidence'], 1, f"evidence_{i+1}_2"))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fppub_sql, (fp_id, pub_id))

        # linked_to
        cursor.execute(featprop_sql, (sf_id, cvterm_id['linked_to'], 0, f"linked_to_{i+1}_1"))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fppub_sql, (fp_id, pub_id))
        cursor.execute(featprop_sql, (sf_id, cvterm_id['linked_to'], 1, f"linked_to_{i+1}_2"))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fppub_sql, (fp_id, pub_id))

        # featue relationship prop pubs
        cursor.execute(feat_rel_sql, (sf_id, feature_id['symbol-{}'.format(i+1)], cvterm_id['associated_with']))
        fr_id = cursor.fetchone()[0]

        cursor.execute(frp_sql, (fr_id, cvterm_id['score'], i+1, i+1))
        frp_id = cursor.fetchone()[0]

        cursor.execute(frpub_sql, (frp_id, pub_id))
