####################################################################################################################################
#     Module to load Humanhealth data.
#
#
#     Humanhealth
#     -----------
#       Create 10 of these
#       hh1->hh5 will be parents
#       hh6->hh10 will be sub entitys of these
#       hh6 belongs_to hh1
#       hh7 belongs_to hh2 etc
#
#       associate hh1 with hh[2345]
#
#     So what did we create?
#     SELECT hs.uniquename, c.name, ho.uniquename
#       FROM humanhealth_relationship hr, humanhealth ho, humanhealth hs, cvterm c
#       WHERE hr.subject_id = hs.humanhealth_id AND
#           hr.object_id = ho.humanhealth_id AND
#           hr.type_id = c.cvterm_id;
#
#      uniquename  |      name       | uniquename
#     -------------+-----------------+-------------
#      FBhh0000005 | associated_with | FBhh0000001
#      FBhh0000004 | associated_with | FBhh0000001
#      FBhh0000003 | associated_with | FBhh0000001
#      FBhh0000002 | associated_with | FBhh0000001
#      FBhh0000006 | belongs_to      | FBhh0000001
#      FBhh0000007 | belongs_to      | FBhh0000002
#      FBhh0000008 | belongs_to      | FBhh0000003
#      FBhh0000009 | belongs_to      | FBhh0000004
#      FBhh0000010 | belongs_to      | FBhh0000005
#
#     Humanhealth Features
#     --------------------
#       Add humanhealth features and props for first 5 (X=>[1..5])
#       Add hh_feat hhX and [Hsap\symbol-X,           Mmus\symbol-X,          Zzzz\symbol-X,         symbol-X]
#                with props ['human_gene_implicated', 'other_mammalian_gene', 'syn_gene_implicated', 'dmel_gene_implicated']
#
#     SELECT hh.name, f.name, c.name, fp.value
#       FROM humanhealth_feature hf, humanhealth hh, feature f, humanhealth_featureprop fp, cvterm c
#       WHERE hf.feature_id = f.feature_id AND
#             hf.humanhealth_id = hh.humanhealth_id AND
#             fp.humanhealth_feature_id = hf.humanhealth_feature_id AND
#             fp.type_id = c.cvterm_id;
#
#         name    |     name      |          name          |       value
#     ------------+---------------+------------------------+-------------------
#      hh-name-1  | al-symbol-5   | human_disease_relevant | Comment 1
#      hh-name-2  | al-symbol-5   | human_disease_relevant | Comment 2
#      hh-name-3  | al-symbol-5   | human_disease_relevant | Comment 3
#      hh-name-4  | al-symbol-5   | human_disease_relevant | Comment 4
#      hh-name-5  | al-symbol-5   | human_disease_relevant | Comment 5
#      hh-name-6  | al-symbol-5   | human_disease_relevant | Comment 6
#      hh-name-7  | al-symbol-5   | human_disease_relevant | Comment 7
#      hh-name-8  | al-symbol-5   | human_disease_relevant | Comment 8
#      hh-name-9  | al-symbol-5   | human_disease_relevant | Comment 9
#      hh-name-10 | al-symbol-5   | human_disease_relevant | Comment 10
#      hh-name-1  | Hsap\symbol-1 | human_gene_implicated  | blank
#      hh-name-1  | Mmus\symbol-1 | other_mammalian_gene   | blank
#      hh-name-1  | Zzzz\symbol-1 | syn_gene_implicated    | blank
#      hh-name-1  | symbol-1      | dmel_gene_implicated   | blank
#      hh-name-1  | symbol-1      | hh_ortholog_comment    | Another Comment 1
#      hh-name-2  | Hsap\symbol-2 | human_gene_implicated  | blank
#      hh-name-2  | Mmus\symbol-2 | other_mammalian_gene   | blank
#      hh-name-2  | Zzzz\symbol-2 | syn_gene_implicated    | blank
#      hh-name-2  | symbol-2      | dmel_gene_implicated   | blank
#      hh-name-2  | symbol-2      | hh_ortholog_comment    | Another Comment 2
#      hh-name-3  | Hsap\symbol-3 | human_gene_implicated  | blank
#      hh-name-3  | Mmus\symbol-3 | other_mammalian_gene   | blank
#      hh-name-3  | Zzzz\symbol-3 | syn_gene_implicated    | blank
#      hh-name-3  | symbol-3      | dmel_gene_implicated   | blank
#      hh-name-3  | symbol-3      | hh_ortholog_comment    | Another Comment 3
#      hh-name-4  | Hsap\symbol-4 | human_gene_implicated  | blank
#      hh-name-4  | Mmus\symbol-4 | other_mammalian_gene   | blank
#      hh-name-4  | Zzzz\symbol-4 | syn_gene_implicated    | blank
#      hh-name-4  | symbol-4      | dmel_gene_implicated   | blank
#      hh-name-4  | symbol-4      | hh_ortholog_comment    | Another Comment 4
#      hh-name-5  | Hsap\symbol-5 | human_gene_implicated  | blank
#      hh-name-5  | Mmus\symbol-5 | other_mammalian_gene   | blank
#      hh-name-5  | Zzzz\symbol-5 | syn_gene_implicated    | blank
#      hh-name-5  | symbol-5      | dmel_gene_implicated   | blank
#      hh-name-5  | symbol-5      | hh_ortholog_comment    | Another Comment 5
#     (35 rows)
#
#
#     Humanhealth Dbxrefs
#     -------------------
#     SELECT hh.name, d.name, dx.accession, cv.name, hdp.value
#       FROM humanhealth hh, humanhealth_dbxref hd, humanhealth_dbxrefprop hdp, humanhealth_dbxrefprop_pub hdpp,
#            dbxref dx, db d, cvterm cv, pub p
#       WHERE hh.humanhealth_id = hd.humanhealth_id AND
#             hdpp.humanhealth_dbxrefprop_id = hdp.humanhealth_dbxrefprop_id AND
#             hdpp.pub_id = p.pub_id AND
#             hd.dbxref_id = dx.dbxref_id AND
#             dx.db_id = d.db_id AND
#             hdp.humanhealth_dbxref_id = hd.humanhealth_dbxref_id AND
#             cv.cvterm_id = hdp.type_id LIMIT 24;
#        name    |      name      | accession |         name         |   value
#     -----------+----------------+-----------+----------------------+------------
#      hh-name-1 | OMIM_PHENOTYPE | 111111    | hh2c_link            | test value
#      hh-name-1 | OMIM_PHENOTYPE | 111111    | OMIM_pheno_table     | test value
#      hh-name-1 | OMIM_PHENOTYPE | 666666    | hh2c_link            | test value
#      hh-name-1 | OMIM_PHENOTYPE | 666666    | OMIM_pheno_table     | test value
#      hh-name-1 | HGNC           | 1         | data_link            | test value
#      hh-name-1 | HGNC           | 1         | hgnc_link            | test value
#      hh-name-1 | HGNC           | 1         | hh_ortho_rel_comment | test value
#      hh-name-1 | HGNC           | 6         | data_link            | test value
#      hh-name-1 | HGNC           | 6         | hgnc_link            | test value
#      hh-name-1 | HGNC           | 6         | hh_ortho_rel_comment | test value
#      hh-name-1 | BDSC_HD        | 1         | data_link_bdsc       | test value
#      hh-name-1 | BDSC_HD        | 6         | data_link_bdsc       | test value
#      hh-name-2 | OMIM_PHENOTYPE | 222222    | hh2c_link            | test value
#      hh-name-2 | OMIM_PHENOTYPE | 222222    | OMIM_pheno_table     | test value
#      hh-name-2 | OMIM_PHENOTYPE | 777777    | hh2c_link            | test value
#      hh-name-2 | OMIM_PHENOTYPE | 777777    | OMIM_pheno_table     | test value
#      hh-name-2 | HGNC           | 2         | data_link            | test value
#      hh-name-2 | HGNC           | 2         | hgnc_link            | test value
#      hh-name-2 | HGNC           | 2         | hh_ortho_rel_comment | test value
#      hh-name-2 | HGNC           | 7         | data_link            | test value
#      hh-name-2 | HGNC           | 7         | hgnc_link            | test value
#      hh-name-2 | HGNC           | 7         | hh_ortho_rel_comment | test value
#      hh-name-2 | BDSC_HD        | 2         | data_link_bdsc       | test value
#      hh-name-2 | BDSC_HD        | 7         | data_link_bdsc       | test value
###################################################################################


def add_humanhealth_data(cursor, feature_id, cvterm_id, db_dbxref, gene_id, pub_id, human_id):
    hh_sql = """ INSERT INTO humanhealth (name, uniquename, organism_id) VALUES (%s, %s, %s) RETURNING humanhealth_id """
    hh_fs_sql = """ INSERT INTO humanhealth_synonym (synonym_id, humanhealth_id,  pub_id, is_current) VALUES (%s, %s, %s, %s) """
    hh_f_sql = """ INSERT INTO humanhealth_feature (humanhealth_id, feature_id, pub_id) VALUES (%s, %s, %s) RETURNING humanhealth_feature_id """
    hh_fp_sql = """ INSERT INTO humanhealth_featureprop (humanhealth_feature_id, type_id, value) VALUES (%s, %s, %s) """
    hh_pub_sql = """ INSERT INTO humanhealth_pub (humanhealth_id, pub_id) VALUES (%s, %s) """
    f_hh_dbxref_sql = """ INSERT INTO feature_humanhealth_dbxref (feature_id, humanhealth_dbxref_id, pub_id) VALUES (%s, %s, %s) """
    hh_rel_sql = """ INSERT INTO humanhealth_relationship (subject_id, object_id, type_id) VALUES (%s, %s, %s) """
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    hh_prop_sql = """ INSERT INTO humanhealthprop (humanhealth_id, type_id, value) VALUES (%s, %s, %s) """

    ###################################################
    # Create 10 Humanhealths with synonyms and type etc
    ###################################################
    for i in range(10):
        print("Adding human health {}".format(i+1))
        # create human health feature, No need to attach to gene for now.
        cursor.execute(hh_sql, ("hh-name-{}".format(i+1), 'FBhh:temp_0', human_id))
        feature_id["hh-symbol-{}".format(i+1)] = hh_id = cursor.fetchone()[0]

        # set the type
        hh_type = cvterm_id['category']
        if i < 5:
            value = 'parent-entity'
        else:
            value = 'sub-entity'
        hh_id = feature_id["hh-symbol-{}".format(i+1)]
        cursor.execute(hh_prop_sql, (hh_id, hh_type, value))

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

    ######################
    # Adding Gene Features
    ######################
    for i in range(5):
        hh_id = feature_id["hh-symbol-{}".format(i+1)]
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

    ###################
    # Add relationships
    ###################
    for i in range(5):
        # add belongs to
        cursor.execute(hh_rel_sql, (feature_id["hh-symbol-{}".format(i+6)], feature_id["hh-symbol-{}".format(i+1)], cvterm_id['belongs_to']))
        print("{} belongs to {}".format("hh-name-{}".format(i+6), "hh-name-{}".format(i+1)))

        # add associated with
        if i:
            cursor.execute(hh_rel_sql, (feature_id["hh-symbol-{}".format(i+1)], feature_id["hh-symbol-1"], cvterm_id['associated_with']))
            print("{} associated with {}".format("hh-symbol-1", "hh-name-{}".format(i+1)))

    #########################
    # Add humanhealth dbxrefs
    #########################
    for i in range(5):
        # Add 2 OMIM_PHENOTYPE dbxrefs to hh2c_link and OMIM_pheno_table hh_dbxrefs
        cvterms_to_add = [cvterm_id['hh2c_link'],
                          cvterm_id['OMIM_pheno_table']]
        if i < 4:  # OMIM is 6 chars 111111, 222222 -> 999999, 101010
            acc = "{}".format(i+1)*6
            acc2 = "{}".format(i+6)*6
        else:
            acc = "{}".format(i+1)*6
            acc2 = "{}".format(i+6)*3
        hh_id = feature_id["hh-symbol-{}".format(i+1)]
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
