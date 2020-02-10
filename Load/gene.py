##################
# create genes
# including their locations
# and alleles
##################

feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""

gene_sub_count = 0


def create_gene(cursor, organism_name, org_id, gene_count, cvterm_id, feature_id, pub_id, add_alpha=False):
    ####################################
    # Create the genes.
    # To be able to test uniquename lookups wrt symbols we generate the unique names by hane now.
    #
    # So the Dmel gene will look like
    # FBgn0000100 -> symbol-1
    # FBgn0000200 -> symbol-2
    #
    # Other species the name is incremented so:-
    #
    # Hsap\symbol-1 -> FBgn0000101, Hsap\symbol-2 -> FBgn0000201
    # Mmus\symbol-1 -> FBgn0000102
    # Zzzz\symbol-1 -> FBgn0000103
    ###################################
    global gene_sub_count

    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id) VALUES (%s, %s, %s) """
    loc_sql = """ INSERT INTO featureloc (feature_id, srcfeature_id, fmin, fmax, strand) VALUES (%s, %s, %s, %s, %s) """
    fb_code = 'gn'

    unique_name = None
    if add_alpha:
        sgml_name = "genechar-α-<up>0002</up>"
        sym_name = "genechar-alpha-[0002]"
        unique_name = 'FB{}:temp_{}'.format(fb_code, gene_count+1)
    elif organism_name == 'Dmel':
        gene_sub_count = 0
        sgml_name = sym_name = "symbol-{}".format(gene_count+1)
        unique_name = 'FB{}{:07d}'.format(fb_code, ((gene_count+1)*100 + gene_sub_count))
    else:
        gene_sub_count += 1
        sgml_name = sym_name = '{}\\symbol-{}'.format(organism_name, gene_count+1)
        unique_name = 'FB{}{:07d}'.format(fb_code, ((gene_count+1)*100 + gene_sub_count))

    print("Adding gene {} for species {} - syn {}".format(gene_count+1, organism_name, sym_name))

    # create the gene feature
    cursor.execute(feat_sql, (None, org_id, sym_name, unique_name, "ACTG"*5, 20, cvterm_id['gene']))
    feature_id[sym_name] = gene_id = cursor.fetchone()[0]

    # add synonyms
    if organism_name == 'Dmel':
        cursor.execute(syn_sql, ("fullname-{}".format(gene_count+1), cvterm_id['fullname'], "fullname-{}".format(gene_count+1)))
        name_id = cursor.fetchone()[0]
    cursor.execute(syn_sql, (sym_name, cvterm_id['symbol'], sgml_name))
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    if organism_name == 'Dmel':
        cursor.execute(fs_sql, (name_id, gene_id, pub_id))
    cursor.execute(fs_sql, (symbol_id, gene_id, pub_id))

    # now add the feature loc
    cursor.execute(loc_sql, (gene_id, feature_id['2L'], gene_count*100, (gene_count+1)*100, 1))
    return gene_id


def add_gene_data(cursor, organism_id, feature_id, cvterm_id, dbxref_id, pub_id):
    fd_sql = """ INSERT INTO feature_dbxref (feature_id, dbxref_id) VALUES (%s, %s) """
    feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id) VALUES (%s, %s, %s) RETURNING feature_relationship_id """
    alleles = []

    feature_id['gene'] = gene_id = create_gene(cursor, 'Dmel', organism_id['Dmel'], 40, cvterm_id, feature_id, pub_id, add_alpha=True)
    for i in range(10):
        feature_id['gene'] = gene_id = create_gene(cursor, 'Dmel', organism_id['Dmel'], i, cvterm_id, feature_id, pub_id)

        # create mouse and human genes
        create_gene(cursor, 'Hsap', organism_id['Hsap'], i, cvterm_id, feature_id, pub_id)
        create_gene(cursor, 'Mmus', organism_id['Mmus'], i, cvterm_id, feature_id, pub_id)
        create_gene(cursor, 'Zzzz', organism_id['Zzzz'], i, cvterm_id, feature_id, pub_id)

        # add allele for each gene and add feature_relationship
        cursor.execute(feat_sql, (None, organism_id['Dmel'], "al-symbol-{}".format(i+1),
                       'FBal:temp_{}'.format(i), None, 200, cvterm_id['gene']))
        feature_id["al-symbol-{}".format(i+1)] = allele_id = cursor.fetchone()[0]
        alleles.append(allele_id)
        cursor.execute(feat_rel_sql, (allele_id, gene_id, cvterm_id['alleleof']))

        # add ClinVar dbxrefs to allele for testing changing description and removal
        for j in range(5):
            cursor.execute(fd_sql, (allele_id, dbxref_id['ClinVar{}'.format(j+1)]))

    return gene_id
