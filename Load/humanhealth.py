# human health


def add_humanhealth_data(cursor, feature_id, cvterm_id, db_dbxref, gene_id, pub_id, human_id):
    hh_sql = """ INSERT INTO humanhealth (name, uniquename, organism_id) VALUES (%s, %s, %s) RETURNING humanhealth_id """
    hh_fs_sql = """ INSERT INTO humanhealth_synonym (synonym_id, humanhealth_id,  pub_id, is_current) VALUES (%s, %s, %s, %s) """
    hh_f_sql = """ INSERT INTO humanhealth_feature (humanhealth_id, feature_id, pub_id) VALUES (%s, %s, %s) RETURNING humanhealth_feature_id """
    hh_fp_sql = """ INSERT INTO humanhealth_featureprop (humanhealth_feature_id, type_id, value) VALUES (%s, %s, %s) """
    hh_pub_sql = """ INSERT INTO humanhealth_pub (humanhealth_id, pub_id) VALUES (%s, %s) """
    f_hh_dbxref_sql = """ INSERT INTO feature_humanhealth_dbxref (feature_id, humanhealth_dbxref_id, pub_id) VALUES (%s, %s, %s) """
    hh_rel_sql = """ INSERT INTO humanhealth_relationship (subject_id, object_id, type_id) VALUES (%s, %s, %s) """
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """

    for i in range(5):
        print("Adding human health {}".format(i+1))
        # create human health feature, No need to attach to gene for now.
        cursor.execute(hh_sql, ("hh-name-{}".format(i+1), 'FBhh:temp_0', human_id))
        feature_id["hh-symbol-{}".format(i+1)] = hh_id = cursor.fetchone()[0]

        # Add relationships
        # hh1 associated with hh[2345]
        # hh5 belongs to hh4 belongs to hh3 .....
        if i:
            cursor.execute(hh_rel_sql, (feature_id["hh-symbol-{}".format(i)], hh_id, cvterm_id['belongs_to']))
            print("{} belongs to {}".format("hh-name-{}".format(i+1), "hh-name-{}".format(i)))
            cursor.execute(hh_rel_sql, (hh_id, feature_id["hh-symbol-1"], cvterm_id['associated_with']))
            print("{} associated with {}".format("hh-symbol-1", "hh-name-{}".format(i+1)))

        # add humanheath_pub
        cursor.execute(hh_pub_sql, (hh_id, pub_id))

        # add synonyms
        cursor.execute(syn_sql, ("hh-fullname-{}".format(i+1), cvterm_id['fullname'], "hh-fullname-{}".format(i+1)))
        name_id = cursor.fetchone()[0]
        cursor.execute(syn_sql, ("hh-symbol-{}".format(i+1), cvterm_id['symbol'], "hh-symbol-{}".format(i+1)))
        symbol_id = cursor.fetchone()[0]

        # add feature_synonym
        cursor.execute(hh_fs_sql, (name_id, hh_id, pub_id, True))
        cursor.execute(hh_fs_sql, (symbol_id, hh_id, pub_id, True))

        # add humanhealth_feature + prop to allele.
        cursor.execute(hh_f_sql, (hh_id, feature_id['allele'], pub_id))
        hh_f_id = cursor.fetchone()[0]
        cursor.execute(hh_fp_sql, (hh_f_id, cvterm_id['human_disease_relevant'], 'Comment {}'.format(i+1)))

        # create various hh feature props
        cvterm_to_sym = {'human_gene_implicated': 'Hsap\\symbol',
                         'other_mammalian_gene': 'Mmus\\symbol',
                         'syn_gene_implicated': 'Zzzz\\symbol',
                         'dmel_gene_implicated': 'symbol'}
        for cv_key in cvterm_to_sym.keys():
            # create hh_feat
            cursor.execute(hh_f_sql, (hh_id, feature_id['{}-{}'.format(cvterm_to_sym[cv_key], i+1)], pub_id))
            hh_f_id = cursor.fetchone()[0]
            # add prop for hh_feat
            cursor.execute(hh_fp_sql, (hh_f_id, cvterm_id[cv_key], 'blank'))
            if cv_key == 'dmel_gene_implicated':
                cursor.execute(hh_fp_sql, (hh_f_id, cvterm_id['hh_ortholog_comment'], 'Another Comment {}'.format(i+1)))

        # Add 2 OMIM_PHENOTYPE dbxrefs to hh2c_link and OMIM_pheno_table hh_dbxrefs
        cvterms_to_add = [cvterm_id['hh2c_link'],
                          cvterm_id['OMIM_pheno_table']]
        if i < 4:  # OMIM is 6 chars 111111, 222222 -> 999999, 101010
            acc = "{}".format(i+1)*6
            acc2 = "{}".format(i+6)*6
        else:
            acc = "{}".format(i+1)*6
            acc2 = "{}".format(i+6)*3
        create_hh_dbxref(hh_id, db_dbxref['OMIM_PHENOTYPE'][acc], cvterms_to_add, cursor, pub_id)
        create_hh_dbxref(hh_id, db_dbxref['OMIM_PHENOTYPE'][acc2], cvterms_to_add, cursor, pub_id)

        # Add 2 HGNC dbxrefs to data_link, hgnc_link and hh_ortho_rel_comment
        # also add feature_humanhealth_dbxref
        cvterms_to_add = [cvterm_id['data_link'],
                          cvterm_id['hgnc_link'],
                          cvterm_id['hh_ortho_rel_comment']]
        hh_dbxref_id = create_hh_dbxref(hh_id, db_dbxref['HGNC']["{}".format(i+1)], cvterms_to_add, cursor, pub_id)
        cursor.execute(f_hh_dbxref_sql, (gene_id, hh_dbxref_id, pub_id))
        hh_dbxref_id = create_hh_dbxref(hh_id, db_dbxref['HGNC']["{}".format(i+6)], cvterms_to_add, cursor, pub_id)
        cursor.execute(f_hh_dbxref_sql, (gene_id, hh_dbxref_id, pub_id))

        # Add 2 BDSC_HD
        cvterms_to_add = [cvterm_id['data_link_bdsc']]
        create_hh_dbxref(hh_id, db_dbxref['BDSC_HD']["{}".format(i+1)], cvterms_to_add, cursor, pub_id)
        create_hh_dbxref(hh_id, db_dbxref['BDSC_HD']["{}".format(i+6)], cvterms_to_add, cursor, pub_id)


def create_hh_dbxref(hh_id, dbxref_id, types, cursor, pub_id):
    """
    Add humanhealth_dbxrefproppub, humanhealth_dbxrefprop, humanhealth_dbxref.
    """
    hh_dbxref_sql = """ INSERT INTO humanhealth_dbxref (humanhealth_id, dbxref_id) VALUES (%s, %s) RETURNING humanhealth_dbxref_id """
    hh_dbxrefprop_sql = """ INSERT INTO humanhealth_dbxrefprop (humanhealth_dbxref_id, type_id, rank, value) VALUES (%s, %s, %s, %s)"""
    hh_dbxrefprop_sql += """  RETURNING humanhealth_dbxrefprop_id """
    hh_dbxrefproppub_sql = """ INSERT INTO humanhealth_dbxrefprop_pub (humanhealth_dbxrefprop_id, pub_id) VALUES (%s, %s) """
    cursor.execute(hh_dbxref_sql, (hh_id, dbxref_id))
    hh_dbxref_id = cursor.fetchone()[0]

    for type_id in types:
        cursor.execute(hh_dbxrefprop_sql, (hh_dbxref_id, type_id, 0, "test value"))
        hh_dbxrefprop_id = cursor.fetchone()[0]

        cursor.execute(hh_dbxrefproppub_sql, (hh_dbxrefprop_id, pub_id))
    return hh_dbxref_id
