"""Create driver data."""

feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""


def add_driver_data(cursor, org_dict, feature_id, cvterm_id, dbxref_id, pub_id, db_id):
    """Add all the drivers needed for testing."""
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id) VALUES (%s, %s, %s) """
    feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id) VALUES (%s, %s, %s) RETURNING feature_relationship_id """

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
