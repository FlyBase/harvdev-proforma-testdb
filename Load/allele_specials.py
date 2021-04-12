"""Create data for allele merging tests.

create 5 genes each having 3 alleles

each allele should have :-
    transcript ,           FBal is Obj
    transgenic_transposon, FBal is Sub
    DNA_segment,           FBal is Sub


example
   FBgn0086784 stmA
     FBal0197755 stmA[EGFP]
       FBtp0023359 P{stmA-EGFP.H}
       FBtr0480549 stmA[EGFP]RA
       FBto0000027 EGFP

"""
gene_count = 50000
allele_count = 50000


def create_merge_allele(cursor, org_dict, feature_id, cvterm_id, db_id, unattrib_pub):
    global gene_count, allele_count
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

    org_id = org_dict['Dmel']
    """
    tool = tool1
       FBgn0086784 merge_geneX
       FBal0197755 merge_geneX[tool1]
       FBtp0023359 P{merge_geneX-tool1.H}
       FBtr0480549 merge_geneX[tool1]RA
       FBto0000027 tool1
    """
    tool_count = 0
    for i in range(5):
        gene_count += 1
        gene_name = "merge_gene{}".format(i+1)
        gene_unique_name = 'FB{}{:07d}'.format('gn', ((gene_count+1)*100))
        print(gene_unique_name)
        # create dbxref,  accession -> uniquename
        cursor.execute(dbxref_sql, (db_id['FlyBase'], gene_unique_name))
        dbxref_id = cursor.fetchone()[0]

        # create the gene feature
        cursor.execute(feat_sql, (dbxref_id, org_id, gene_name, gene_unique_name, "ACTG"*5, 20, cvterm_id['gene']))
        gene_id = cursor.fetchone()[0]

        # create pub
        cursor.execute(pub_sql, (cvterm_id['journal'], 'merge_title_{}'.format(i+1), 'FB{}{:07d}'.format('rf', gene_count),
                                 '2020', 'mini_{}'.format(gene_count)))
        pub_id = cursor.fetchone()[0]

        # add synonym for gene
        cursor.execute(syn_sql, (gene_name, cvterm_id['symbol'], gene_name))
        symbol_id = cursor.fetchone()[0]

        # add feature_synonym for gene
        cursor.execute(fs_sql, (symbol_id, gene_id, pub_id))
        cursor.execute(fs_sql, (symbol_id, gene_id, feature_id['unattributed']))

        # now add 3 alleles for each
        for j in range(3):
            allele_count += 1
            tool_count += 1
            tool_name = "Clk{}".format(tool_count)  # prviously j ?
            allele_name = "{}[{}]".format(gene_name, tool_name)
            sgml_name = "{}<up>{}</up>".format(gene_name, tool_name)
            allele_unique_name = 'FB{}{:07d}'.format('al', (allele_count))

            print(" gene {} {}: allele {} {}".format(gene_name, gene_unique_name, allele_name, allele_unique_name))

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

            # a dd feature_synonym for allele
            cursor.execute(fs_sql, (symbol_id, allele_id, pub_id))
            cursor.execute(fs_sql, (symbol_id, allele_id, feature_id['unattributed']))

            # add feature pub for allele
            cursor.execute(fp_sql, (allele_id, pub_id))

            # feature relationship gene and allele
            cursor.execute(feat_rel_sql, (allele_id, gene_id, cvterm_id['alleleof']))
            feat_rel = cursor.fetchone()[0]

            # feat rel pub
            cursor.execute(frpub_sql, (feat_rel, pub_id))

            ###################################
            # add tool FBto 'engineered_region'
            ####################################
            tool_unique_name = 'FB{}{:07d}'.format('to', (allele_count))

            # create dbxref,  accession -> uniquename
            cursor.execute(dbxref_sql, (db_id['FlyBase'], tool_unique_name))
            dbxref_id = cursor.fetchone()[0]

            cursor.execute(feat_sql, (dbxref_id, org_id, tool_name, tool_unique_name, "", 0, cvterm_id['engineered_region']))
            tool_id = cursor.fetchone()[0]

            # add feature pub for tool
            cursor.execute(fp_sql, (tool_id, pub_id))

            # feature relationship tool and allele
            cursor.execute(feat_rel_sql, (allele_id, tool_id, cvterm_id['associated_with']))
            feat_rel = cursor.fetchone()[0]

            # feat rel pub
            cursor.execute(frpub_sql, (feat_rel, pub_id))

            ######################################
            # Add FBtr 'mRNA' to this allele (UNATTRIBUTED pub)
            ######################################
            trans_unique_name = 'FB{}{:07d}'.format('tr', (allele_count))
            trans_name = "{}[ZR]".format(allele_name)

            # create dbxref,  accession -> uniquename
            cursor.execute(dbxref_sql, (db_id['FlyBase'], trans_unique_name))
            dbxref_id = cursor.fetchone()[0]

            cursor.execute(feat_sql, (dbxref_id, org_id, trans_name, trans_unique_name, "", 0, cvterm_id['mRNA']))
            trans_id = cursor.fetchone()[0]

            # add feature pub for transcript
            cursor.execute(fp_sql, (trans_id, pub_id))

            # feature relationship transcript and allele
            cursor.execute(feat_rel_sql, (trans_id, allele_id, cvterm_id['associated_with']))
            feat_rel = cursor.fetchone()[0]

            # feat rel pub
            cursor.execute(frpub_sql, (feat_rel, unattrib_pub))

            ############################################
            # add FBtp 'transgenic_transposable_element'
            ############################################
            tte_unique_name = 'FB{}{:07d}'.format('tp', (allele_count))
            tte_name = 'P{}{}-{}.H{}'.format('{', tool_name, gene_name, '}')
            print("transgenic_transposable_element {} {}".format(tte_unique_name, tte_name))
            # create dbxref,  accession -> uniquename
            cursor.execute(dbxref_sql, (db_id['FlyBase'], tte_unique_name))
            dbxref_id = cursor.fetchone()[0]

            cursor.execute(feat_sql, (dbxref_id, org_id, tte_name, tte_unique_name, "", 0, cvterm_id['transgenic_transposable_element']))
            tte_id = cursor.fetchone()[0]

            # add synonym for tp
            cursor.execute(syn_sql, (tte_name, cvterm_id['symbol'], tte_name))
            symbol_id = cursor.fetchone()[0]

            # add feature_synonym for tp
            cursor.execute(fs_sql, (symbol_id, tte_id, pub_id))
            # cursor.execute(fs_sql, (symbol_id, allele_id, feature_id['unattributed']))

            # add feature pub for tool
            cursor.execute(fp_sql, (tte_id, pub_id))

            # feature relationship tool and allele
            cursor.execute(feat_rel_sql, (allele_id, tte_id, cvterm_id['associated_with']))
            feat_rel = cursor.fetchone()[0]

            # feat rel pub
            cursor.execute(frpub_sql, (feat_rel, pub_id))


def create_allele_GA90(cursor, org_dict, feature_id, cvterm_id, db_id, unattrib_pub):
    """Add test data for GA90 tests."""
    global gene_count, allele_count
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

    org_id = org_dict['Dmel']

    for i in range(3):
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


def create_gene_allele_for_GA10(cursor, org_dict, feature_id, cvterm_id, db_id, unattrib_pub):
    """Add data for GA10 tests."""
    global gene_count, allele_count
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

    org_id = org_dict['Dmel']
    for i in range(5):
        gene_count += 1
        gene_name = "GA10gene{}".format(i+1)
        gene_unique_name = 'FB{}{:07d}'.format('gn', ((gene_count+1)*100))
        print(gene_unique_name)
        # create dbxref,  accession -> uniquename
        cursor.execute(dbxref_sql, (db_id['FlyBase'], gene_unique_name))
        dbxref_id = cursor.fetchone()[0]

        # create the gene feature
        cursor.execute(feat_sql, (dbxref_id, org_id, gene_name, gene_unique_name, "ACTG"*5, 20, cvterm_id['gene']))
        gene_id = cursor.fetchone()[0]

        # create pub
        cursor.execute(pub_sql, (cvterm_id['journal'], 'GA10_title_{}'.format(i+1), 'FB{}{:07d}'.format('rf', gene_count),
                                 '2020', 'mini_{}'.format(gene_count)))
        pub_id = cursor.fetchone()[0]

        # add synonym for gene
        cursor.execute(syn_sql, (gene_name, cvterm_id['symbol'], gene_name))
        symbol_id = cursor.fetchone()[0]

        # add feature_synonym for gene
        cursor.execute(fs_sql, (symbol_id, gene_id, pub_id))
        cursor.execute(fs_sql, (symbol_id, gene_id, feature_id['unattributed']))

        # now add 3 alleles for each
        for j in range(3):
            allele_count += 1
            tool_name = "GA10Tool{}".format(j)
            allele_name = "{}[{}]".format(gene_name, tool_name)
            sgml_name = "{}<up>{}</up>".format(gene_name, tool_name)
            allele_unique_name = 'FB{}{:07d}'.format('al', (allele_count))

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

            ############################################
            # add FBtp 'transgenic_transposable_element'
            ############################################
            tte_unique_name = 'FBtp:temp_1'
            tte_name = 'P{}{}-{}.H{}'.format('{', tool_name, gene_name, '}')
            print(" gene {} {}: allele {} {} tp:{}".format(gene_name, gene_unique_name, allele_name, allele_unique_name, tte_name))
            # create dbxref,  accession -> uniquename
            # cursor.execute(dbxref_sql, (db_id['FlyBase'], tte_unique_name))
            # dbxref_id = cursor.fetchone()[0]

            cursor.execute(feat_sql, (None, org_id, tte_name, tte_unique_name, "", 0, cvterm_id['transgenic_transposable_element']))
            tte_id = cursor.fetchone()[0]

            # add synonym for tp
            cursor.execute(syn_sql, (tte_name, cvterm_id['symbol'], tte_name))
            symbol_id = cursor.fetchone()[0]

            # add feature_synonym for tp
            cursor.execute(fs_sql, (symbol_id, tte_id, pub_id))
            # cursor.execute(fs_sql, (symbol_id, allele_id, feature_id['unattributed']))

            # add feature pub for tool
            cursor.execute(fp_sql, (tte_id, pub_id))

            # feature relationship tool and allele
            cursor.execute(feat_rel_sql, (allele_id, tte_id, cvterm_id['associated_with']))
            feat_rel = cursor.fetchone()[0]

            # feat rel pub
            cursor.execute(frpub_sql, (feat_rel, pub_id))


def create_allele_props(cursor, org_dict, feature_id, cvterm_id, db_id, pub_id):
    """Create allele props.

    For testing bangc/d operations.
    """
    global gene_count, allele_count
    dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id """
    feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""
    # fd_sql = """ INSERT INTO feature_dbxref (feature_id, dbxref_id) VALUES (%s, %s) """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id) VALUES (%s, %s, %s) """
    feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id)
                       VALUES (%s, %s, %s) RETURNING feature_relationship_id """
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    frpub_sql = """ INSERT INTO feature_relationship_pub (feature_relationship_id, pub_id) VALUES (%s, %s) """
    # pub_sql = """ INSERT INTO pub (type_id, title, uniquename, pyear, miniref) VALUES (%s, %s, %s, %s, %s) RETURNING pub_id """
    fp_sql = """ INSERT INTO feature_pub (feature_id, pub_id) VALUES (%s, %s) """
    fprop_sql = """ INSERT INTO featureprop (feature_id, type_id, value, rank) VALUES (%s, %s, %s, %s) RETURNING featureprop_id """
    fpp_sql = """ INSERT INTO featureprop_pub (featureprop_id, pub_id) VALUES (%s, %s) """

    org_id = org_dict['Dmel']
    for i in range(5):  # 5 genes should be enough for now.
        gene_count += 1
        gene_name = "geneprop{}".format(i+1)
        gene_unique_name = 'FB{}{:07d}'.format('gn', ((gene_count+1)*100))
        print(gene_unique_name)
        # create dbxref,  accession -> uniquename
        cursor.execute(dbxref_sql, (db_id['FlyBase'], gene_unique_name))
        dbxref_id = cursor.fetchone()[0]

        # create the gene feature
        cursor.execute(feat_sql, (dbxref_id, org_id, gene_name, gene_unique_name, "ACTG"*5, 20, cvterm_id['gene']))
        gene_id = cursor.fetchone()[0]

        # # create pub
        # cursor.execute(pub_sql, (cvterm_id['journal'], 'GA10_title_{}'.format(i+1), 'FB{}{:07d}'.format('rf', gene_count),
        #                          '2020', 'mini_{}'.format(gene_count)))
        # pub_id = cursor.fetchone()[0]

        # add synonym for gene
        cursor.execute(syn_sql, (gene_name, cvterm_id['symbol'], gene_name))
        symbol_id = cursor.fetchone()[0]

        # add feature_synonym for gene
        cursor.execute(fs_sql, (symbol_id, gene_id, pub_id))
        cursor.execute(fs_sql, (symbol_id, gene_id, feature_id['unattributed']))

        # now add 1 alleles for each
        for j in range(1):
            allele_count += 1
            tool_name = "{}".format(j)
            allele_name = "{}[{}]".format(gene_name, tool_name)
            sgml_name = "{}<up>{}</up>".format(gene_name, tool_name)
            allele_unique_name = 'FB{}{:07d}'.format('al', (allele_count))

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

            # {field}: [cvtermprop, value] # value will have 1 {} for substitution or it will be None
            props = {'GA12a': ['aminoacid_rep', r'Amino acid replacement: Q100{}term prop 12a'],
                     'GA12a-2': ['nucleotide_sub', r'Nucleotide substitution: {}'],
                     'GA12b': ['molecular_info', r'@Tool-sym-{}@ some test prop wrt 12b'],
                     'GA30f': ['propagate_transgenic_uses', None],
                     'GA85': ['deliberate_omission', 'default comment'],
                     'GA36': ['disease_associated', None]}
            for item in props.values():
                if item[1]:
                    value = item[1].format(allele_count)
                else:
                    value = item[1]
                cursor.execute(fprop_sql, (allele_id, cvterm_id[item[0]], value, 0))
                print("pub='{}', Gene:'{}', Allele:'{}':- prop='{}', value='{}'".format(pub_id, gene_name, allele_name, item[0], value))
                fp_id = cursor.fetchone()[0]
                cursor.execute(fpp_sql, (fp_id, pub_id))

            # add relationships
            rela = {'GA11': ['progenitor', [r'TP{1}', r'TP{2}']]}
            for item in rela.values():
                for feat_name in item[1]:
                    # create relationship between allele and feature (from name)
                    cursor.execute(feat_rel_sql, (feature_id[feat_name], allele_id, cvterm_id[item[0]]))
                    feat_rel = cursor.fetchone()[0]

                    # feat rel pub
                    cursor.execute(frpub_sql, (feat_rel, pub_id))
