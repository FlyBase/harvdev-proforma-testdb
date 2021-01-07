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
from harvdev_utils.char_conversions import sgml_to_unicode


def create_merge_allele(cursor, org_dict, feature_id, cvterm_id, db_id, unattrib_pub):
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

    gene_count = 50000
    allele_count = 50000
    org_id = org_dict['Dmel']
    """
    tool = tool1
       FBgn0086784 merge_geneX
       FBal0197755 merge_geneX[tool1]
       FBtp0023359 P{merge_geneX-tool1.H}
       FBtr0480549 merge_geneX[tool1]RA
       FBto0000027 tool1
    """
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
            tool_name = "Clk{}".format(j)
            allele_name = "{}[{}]".format(gene_name, tool_name)
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
            allele_sgml = sgml_to_unicode(allele_name)
            cursor.execute(syn_sql, (allele_name, cvterm_id['symbol'], allele_sgml))
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

            # create dbxref,  accession -> uniquename
            cursor.execute(dbxref_sql, (db_id['FlyBase'], tte_unique_name))
            dbxref_id = cursor.fetchone()[0]

            cursor.execute(feat_sql, (dbxref_id, org_id, tte_name, tte_unique_name, "", 0, cvterm_id['transgenic_transposable_element']))
            tte_id = cursor.fetchone()[0]

            # add feature pub for tool
            cursor.execute(fp_sql, (tte_id, pub_id))

            # feature relationship tool and allele
            cursor.execute(feat_rel_sql, (allele_id, tte_id, cvterm_id['associated_with']))
            feat_rel = cursor.fetchone()[0]

            # feat rel pub
            cursor.execute(frpub_sql, (feat_rel, pub_id))
