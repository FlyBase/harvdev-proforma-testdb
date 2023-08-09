"""Create driver data."""

feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""


def add_driver_data(cursor, org_dict, feature_id, cvterm_id, dbxref_id, pub_id, db_id):
    """Add all the drivers needed for testing."""
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id) VALUES (%s, %s, %s) """
    feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id) VALUES (%s, %s, %s) RETURNING feature_relationship_id """
    feat_cvterm_sql = """INSERT INTO feature_cvterm (feature_id, cvterm_id, pub_id) VALUES (%s, %s, %s)"""
    # create domain
    dom_name = 'DBD'
    cursor.execute(feat_sql, (None, org_dict['Dmel'], 'DBD and LBD domains', 'ss-XP_DBD and LBD domains',
                              "", 0, cvterm_id['polypeptide']))
    feature_id[dom_name] = cursor.fetchone()[0]

    count = gene_count = 500000
    for start in ['Scer\\GAL4', 'Hsap\\RELA']:
        # create gene
        org_id = org_dict[start[:4]]
        sym_name = "{}".format(start)
        count = count + 1
        unique_name = 'FBgn{:07d}'.format(count)
        print("Adding gene {} {} for species {} - syn {}".format(unique_name, gene_count, start[:4], sym_name))
        # create dbxref,  accession -> uniquename
        cursor.execute(dbxref_sql, (db_id['FlyBase'], unique_name))
        dbxref_id = cursor.fetchone()[0]

        # create the gene feature
        cursor.execute(feat_sql, (dbxref_id, org_id, sym_name, unique_name, "ACTG"*5, 20, cvterm_id['gene']))
        feature_id[sym_name] = gene_id = cursor.fetchone()[0]

        for i in range(10):
            # select f.name, cvt2.name, f.uniquename, o.abbreviation, cvt.name
            # from feature_relationship fr, cvterm cvt2, cvterm cvt,  feature f, organism o
            # where f.type_id = cvt2.cvterm_id and fr.object_id = f.feature_id and fr.type_id = cvt.cvterm_id and
            #       o.organism_id = f.organism_id and subject_id = 23124422;
            #        name       |              name               | uniquename  | abbreviation |           name
            # ------------------+---------------------------------+-------------+--------------+---------------------------
            #  Scer\GAL4        | gene                            | FBgn0014445 | Scer         | alleleof
            #  P{GAL4(DBD)-hb}  | transgenic_transposable_element | FBtp0001259 | Ssss         | associated_with
            #  pP{GAL4(DBD)-hb} | engineered_plasmid              | FBmc0001249 | Ssss         | gets_expression_data_from
            #  hb               | gene                            | FBgn0001180 | Dmel         | has_reg_region
            if start == 'Scer\\GAL4':
                gene_name = f'hb{i+1}'
            else:
                gene_name = f'pxn{i + 1}'
            count = count + 1
            al_sym_name = "{}<up>{}.{}</up>".format(start, dom_name, gene_name)
            al_name = "{}[{}.{}]".format(start, dom_name, gene_name)
            unique_name = 'FBal{:07d}'.format(count)
            print("Adding allele {} {} for species {} - syn {}".format(unique_name, count, start[:4], al_name))
            cursor.execute(dbxref_sql, (db_id['FlyBase'], unique_name))
            al_dbxref_id = cursor.fetchone()[0]

            cursor.execute(feat_sql, (al_dbxref_id, org_id, al_name, unique_name, None, 0, cvterm_id['allele']))
            feature_id[al_name] = cursor.fetchone()[0]
            # add synonyms
            cursor.execute(syn_sql, (feature_id[al_name], cvterm_id['symbol'], al_sym_name))
            syn_id = cursor.fetchone()[0]
            cursor.execute(fs_sql, (syn_id, feature_id[al_name], pub_id))

            cursor.execute(syn_sql, (feature_id[al_name], cvterm_id['symbol'], al_sym_name[5:]))  # skip sp name
            syn_id = cursor.fetchone()[0]
            cursor.execute(fs_sql, (syn_id, feature_id[al_name], pub_id))
            #  Scer\GAL4        | gene                            | FBgn0014445 | Scer         | alleleof
            cursor.execute(feat_rel_sql, (feature_id[al_name], feature_id[start], cvterm_id['alleleof']))

            #  hb               | gene                            | FBgn0001180 | Dmel         | has_reg_region
            unique_name = 'FBgn{:07d}'.format(count)
            print("Adding gene {} for species {} - syn {}".format(unique_name, start[:4], gene_name))
            cursor.execute(dbxref_sql, (db_id['FlyBase'], unique_name))
            gene_dbxref_id = cursor.fetchone()[0]
            cursor.execute(feat_sql, (gene_dbxref_id, org_id, gene_name, unique_name, None, 0, cvterm_id['gene']))
            feature_id[gene_name] = cursor.fetchone()[0]
            # add synonym
            # select * from synonym where synonym_id = 6922299;
            # synonym_id | name | type_id | synonym_sgml
            # ------------+-------------------+---------+--------------------------
            # 6922299 | Hsap\RELA[AD.Pxn] | 59978 | Hsap\RELA<up>AD.Pxn</up>
            cursor.execute(syn_sql, (feature_id[gene_name], cvterm_id['symbol'], gene_name))
            syn_id = cursor.fetchone()[0]
            cursor.execute(fs_sql, (syn_id, feature_id[gene_name], pub_id))

            cursor.execute(feat_rel_sql, (feature_id[al_name], feature_id[gene_name], cvterm_id['has_reg_region']))

            #  P{GAL4(DBD)-hb}  | transgenic_transposable_element | FBtp0001259 | Ssss         | associated_with

            #  pP{GAL4(DBD)-hb} | engineered_plasmid              | FBmc0001249 | Ssss         | gets_expression_data_from


    # add split system combination to test merging and deleting etc.
    # NOTE: Using i to get different papers for things to ease tracking later.

    e_sql = """INSERT INTO expression (uniquename, description) values (%s, %s) RETURNING expression_id"""
    fe_sql = """INSERT INTO feature_expression (feature_id, expression_id, pub_id)
                VALUES (%s, %s, %s) RETURNING feature_expression_id"""
    fep_sql = """INSERT INTO feature_expressionprop (feature_expression_id, type_id, value) VALUES (%s, %s, %s)"""
    ec_sql = """INSERT INTO expression_cvterm (expression_id, cvterm_id, cvterm_type_id) VALUES (%s, %s, %s)"""
    fr_sql = """INSERT INTO feature_relationship (subject_id, object_id, type_id) VALUES (%s, %s, %s) RETURNING feature_relationship_id"""
    frp_sql = """INSERT INTO feature_relationship_pub (feature_relationship_id, pub_id) VALUES (%s, %s)"""

    for i in range(4, 9):
        # Scer\\GAL4[DBD.hb1]INTERSECTIONHsap\\RELA[DBD.pxn1]
        # Scer\GAL4<up>DBD.hb1</up>∩Hsap\RELA<up>DBD.pxn1</up>
        co_name = f"Scer\\GAL4[DBD.hb{i}]INTERSECTIONHsap\\RELA[DBD.pxn{i}]"
        co_syn = f"Scer\\GAL4<up>DBD.hb{i}</up>\∩Hsap\\RELA<up>DBD.pxn{i}</up>"
        unique_name = 'FBco{:07d}'.format(i)
        print("Adding split system combination {} {} - syn {}".format(unique_name, i, co_name))
        cursor.execute(dbxref_sql, (db_id['FlyBase'], unique_name))
        co_dbxref_id = cursor.fetchone()[0]

        cursor.execute(feat_sql, (co_dbxref_id, org_dict['Ssss'], co_name, unique_name,
                                  None, 0, cvterm_id['split system combination']))
        feature_id[co_name] = cursor.fetchone()[0]

        # add synonym
        cursor.execute(syn_sql, (feature_id[co_name], cvterm_id['symbol'], co_syn))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, feature_id[co_name], feature_id['unattributed']))

        # add feature cvterms
        # FBco0000001 | Scer\GAL4[DBD.hb1]INTERSECTIONHsap\RELA[DBD.pxn1] | dissociated larval fat cell | FBrf0000001
        # FBco0000001 | Scer\GAL4[DBD.hb1]INTERSECTIONHsap\RELA[DBD.pxn1] | synthetic_sequence          | FBrf0000001
        cursor.execute(feat_cvterm_sql, (feature_id[co_name], cvterm_id['dissociated larval fat cell'],
                                         feature_id[f'CO_paper_{i}']))
        cursor.execute(feat_cvterm_sql, (feature_id[co_name], cvterm_id['synthetic_sequence'],
                                         feature_id[f'CO_paper_{i}']))

        # feature_expression
        cursor.execute(e_sql, ('FBex{:07d}'.format(i), f"desc {i}"))
        exp_id = cursor.fetchone()[0]
        cursor.execute(fe_sql, (feature_id[co_name], exp_id, feature_id[f'CO_paper_{i}']))
        feat_exp_id = cursor.fetchone()[0]

        # feature_expressionprop
        cursor.execute(fep_sql, (feat_exp_id, cvterm_id['comment'], f"Comment {i}"))

        # expression_cvterms
        # if even add anatomy | mesoderm
        # else assay    | in situ
        if (i % 2) == 0:
            cursor.execute(ec_sql, (exp_id, cvterm_id['mesoderm'], cvterm_id['anatomy']))
        else:
            cursor.execute(ec_sql, (exp_id, cvterm_id['in situ'], cvterm_id['assay']))

        # feature relationship and frp
        # FBco0000001 | Scer\GAL4[DBD.hb1]INTERSECTIONHsap\RELA[DBD.pxn1] | partially_produced_by | FBal0500002 | Scer\GAL4[DBD.hb1]  |
        # FBco0000001 | Scer\GAL4[DBD.hb1]INTERSECTIONHsap\RELA[DBD.pxn1] | partially_produced_by | FBal0500013 | Hsap\RELA[DBD.pxn1] |

        cursor.execute(fr_sql, (feature_id[co_name], feature_id[f'Scer\\GAL4[DBD.hb{i}]'], cvterm_id['partially_produced_by']))
        fr_id = cursor.fetchone()[0]
        cursor.execute(frp_sql, (fr_id, feature_id[f'CO_paper_{i}']))
        cursor.execute(fr_sql, (feature_id[co_name], feature_id[f'Hsap\RELA[DBD.pxn{i}]'], cvterm_id['partially_produced_by']))
        fr_id = cursor.fetchone()[0]
        cursor.execute(frp_sql, (fr_id, feature_id[f'CO_paper_{i}']))

