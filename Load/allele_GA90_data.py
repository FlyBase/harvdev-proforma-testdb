"""
Add data for test alleles with GA90 data. i.e. point_mutations

Produce the following relationships
X 1->15
Gene GA90_X
     GA90_X-[1] 'allele'
        GA90_X-[1] 'point_mutation'
"""


def create_allele_GA90(cursor, org_dict, feature_id, cvterm_id, db_id, unattrib_pub):
    """Add test data for GA90 tests."""
    dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id """
    feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""
    # fd_sql = """ INSERT INTO feature_dbxref (feature_id, dbxref_id) VALUES (%s, %s) """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id) VALUES (%s, %s, %s) """
    feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id)
                       VALUES (%s, %s, %s) RETURNING feature_relationship_id """
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    frpub_sql = """ INSERT INTO feature_relationship_pub (feature_relationship_id, pub_id) VALUES (%s, %s) """
    pub_sql = """ INSERT INTO pub (type_id, title, uniquename, pyear, miniref) VALUES (%s, %s, %s, %s, %s) RETURNING pub_id """
    fp_sql = """ INSERT INTO feature_pub (feature_id, pub_id) VALUES (%s, %s) """
    fprop_sql = """ INSERT INTO featureprop (feature_id, type_id, value, rank) VALUES (%s, %s, %s, %s) RETURNING featureprop_id """
    fpp_sql = """ INSERT INTO featureprop_pub (featureprop_id, pub_id) VALUES (%s, %s) """
    loc_sql = """ INSERT INTO featureloc (feature_id, srcfeature_id, fmin, fmax, strand) VALUES (%s, %s, %s, %s, %s) """

    gene_count = 60000
    allele_count = 60000
    org_id = org_dict['Dmel']

    for i in range(15):
        gene_count += 1
        gene_name = "GA90_{}".format(i+1)
        gene_unique_name = 'FB{}{:07d}'.format('gn', ((gene_count+1)*100))
        print(gene_unique_name)
        # create dbxref,  accession -> uniquename
        cursor.execute(dbxref_sql, (db_id['FlyBase'], gene_unique_name))
        dbxref_id = cursor.fetchone()[0]

        # create the gene feature
        cursor.execute(feat_sql, (dbxref_id, org_id, gene_name, gene_unique_name, "ACTG"*5, 20, cvterm_id['gene']))
        gene_id = cursor.fetchone()[0]

        # create pub
        print("Adding Gene, Allele and point mutation data against pub GA90_title_{} FBrf{:07d}".format(i+1, gene_count))
        cursor.execute(pub_sql, (cvterm_id['journal'], 'GA90_title_{}'.format(i+1), 'FB{}{:07d}'.format('rf', gene_count),
                                 '2021', 'mini_{}'.format(gene_count)))
        pub_id = cursor.fetchone()[0]

        # add synonym for gene
        cursor.execute(syn_sql, (gene_name, cvterm_id['symbol'], gene_name))
        symbol_id = cursor.fetchone()[0]

        # add feature_synonym for gene
        cursor.execute(fs_sql, (symbol_id, gene_id, pub_id))
        cursor.execute(fs_sql, (symbol_id, gene_id, feature_id['unattributed']))

        # now add 1 alleles for each
        for j in range(1):
            allele_count += 1
            allele_name = "{}-[{}]".format(gene_name, j+1)
            sgml_name = "{}<up>{}</up>".format(gene_name, j+1)
            allele_unique_name = 'FB{}{:07d}'.format('al', (allele_count))
            print(" gene {} {}: alllele {} {}".format(gene_name, gene_unique_name, allele_name, allele_unique_name))
            if not j:
                # add feature pub for gene
                cursor.execute(fp_sql, (gene_id, pub_id))

            ###########################
            # create the allele feature
            ###########################
            # create dbxref,  accession -> uniquename
            cursor.execute(dbxref_sql, (db_id['FlyBase'], allele_unique_name))
            dbxref_id = cursor.fetchone()[0]

            cursor.execute(feat_sql, (dbxref_id, org_id, allele_name, allele_unique_name, "", 0, cvterm_id['allele']))
            allele_id = cursor.fetchone()[0]

            # add synonym for allele
            cursor.execute(syn_sql, (allele_name, cvterm_id['symbol'], sgml_name))
            symbol_id = cursor.fetchone()[0]

            # add feature_synonym for allele
            cursor.execute(fs_sql, (symbol_id, allele_id, pub_id))
            cursor.execute(fs_sql, (symbol_id, allele_id, feature_id['unattributed']))

            # add feature pub for allele
            cursor.execute(fp_sql, (allele_id, pub_id))

            # feature relationship gene and allele
            cursor.execute(feat_rel_sql, (allele_id, gene_id, cvterm_id['alleleof']))
            feat_rel = cursor.fetchone()[0]

            # feat rel pub
            cursor.execute(frpub_sql, (feat_rel, pub_id))

            ##################################
            # create point mutation for allele NOTE: pm has same name as allele
            ################################## 
            cursor.execute(feat_sql, (None, org_id, allele_name, allele_name, "", 0, cvterm_id['point_mutation']))
            pm_id = cursor.fetchone()[0]

            # # add synonym for point_mutation: ALREADY EXISTS
            # cursor.execute(syn_sql, (allele_name, cvterm_id['symbol'], sgml_name))
            # pm_symbol_id = cursor.fetchone()[0]

            # add feature_synonym for point_mutation
            cursor.execute(fs_sql, (symbol_id, pm_id, pub_id))
            cursor.execute(fs_sql, (symbol_id, pm_id, feature_id['unattributed']))

            # add feature pub for point_mutation
            cursor.execute(fp_sql, (pm_id, pub_id))

            # feature relationship allele and point_mutation
            print("\t allele {} {}: point_mutation {}".format(allele_name, allele_unique_name, allele_name))
            cursor.execute(feat_rel_sql, (pm_id, allele_id, cvterm_id['partof']))
            feat_rel = cursor.fetchone()[0]

            # featureloc for point mutation
            print("\t FeatureLoc to point mutation added to 2L:10..11")
            cursor.execute(loc_sql, (pm_id, feature_id['2L'], 10, 11, 1))

            if (i > 7):
                continue

            # gen bank feature props
            value = "2L_r6:10..11"
            cursor.execute(fprop_sql, (pm_id, cvterm_id['reported_genomic_loc'], value, 0))
            fp_id = cursor.fetchone()[0]
            cursor.execute(fpp_sql, (fp_id, pub_id))

            value = "G1234T"
            for proptype in ('na_change', 'reported_na_change', 'reported_pr_change', 'pr_change', 'linked_to', 'comment'):
                print("\tfeature prop '{}' '{}'".format(proptype, value))
                cursor.execute(fprop_sql, (pm_id, cvterm_id[proptype], value, 0))
                fp_id = cursor.fetchone()[0]
                cursor.execute(fpp_sql, (fp_id, pub_id))
