"""Create driver data."""

feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""


def add_driver_data(cursor, org_dict, feature_id, cvterm_id, dbxref_id, pub_id, db_id):
    """Add all the drivers needed for testing."""
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id) VALUES (%s, %s, %s) """
    feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id) VALUES (%s, %s, %s) RETURNING feature_relationship_id """

    count = gene_count = 400000
    for start in ['Scer\\GAL4', 'Hsap\\RELA']:
        # create gene
        gene_count += 1
        org_id = org_dict[start[:4]]
        sym_name = "{}".format(start)
        unique_name = 'FBgn:{:07d}'.format(gene_count)
        print("Adding gene {} {} for species {} - syn {}".format(unique_name, gene_count, start[:4], sym_name))
        # create dbxref,  accession -> uniquename
        cursor.execute(dbxref_sql, (db_id['FlyBase'], unique_name))
        dbxref_id = cursor.fetchone()[0]

        # create the gene feature
        cursor.execute(feat_sql, (dbxref_id, org_id, sym_name, unique_name, "ACTG"*5, 20, cvterm_id['gene']))
        feature_id[sym_name] = gene_id = cursor.fetchone()[0]

        for i in range(10):
            # create allele/driver.
            count = count + 1
            al_sym_name = "{}[{}]".format(start, count)
            unique_name = 'FBal:{:07d}'.format(count)
            # create dbxref,  accession -> uniquename
            print("Adding allele {} {} for species {} - syn {}".format(unique_name, count, start[:4], sym_name))
            cursor.execute(dbxref_sql, (db_id['FlyBase'], unique_name))
            al_dbxref_id = cursor.fetchone()[0]

            cursor.execute(feat_sql, (al_dbxref_id, org_id, al_sym_name, count, None, 0, cvterm_id['gene']))
            feature_id[al_sym_name] = allele_id = cursor.fetchone()[0]

            # add as feature relationship
            cursor.execute(feat_rel_sql, (allele_id, gene_id, cvterm_id['alleleof']))

            # add synonym for allele
            cursor.execute(syn_sql, (al_sym_name, cvterm_id['symbol'], al_sym_name))
            symbol_id = cursor.fetchone()[0]
            # add feature_synonym for allele
            cursor.execute(fs_sql, (symbol_id, allele_id, pub_id))
