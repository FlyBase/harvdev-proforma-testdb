
"""Functions to generate genes and alleles."""
gene_count = 150000
allele_count = 150000

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


def create_gene(cursor, count, gene_prefix, cvterm_id, org_id, db_id, pub_id, feature_id):
    """Get gene name."""
    global gene_count
    gene_count += 1
    gene_name = "{}{}".format(gene_prefix, count+1)
    gene_unique_name = 'FB{}{:07d}'.format('gn', (gene_count+1))

    # create dbxref,  accession -> uniquename
    cursor.execute(dbxref_sql, (db_id['FlyBase'], gene_unique_name))
    dbxref_id = cursor.fetchone()[0]

    # create the gene feature
    cursor.execute(feat_sql, (dbxref_id, org_id, gene_name, gene_unique_name, "ACTG"*5, 20, cvterm_id['gene']))
    gene_id = feature_id[gene_name] = cursor.fetchone()[0]

    # add synonym for gene
    cursor.execute(syn_sql, (gene_name, cvterm_id['symbol'], gene_name))
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym for gene
    if pub_id != feature_id['unattributed']:
        cursor.execute(fs_sql, (symbol_id, gene_id, pub_id))
    cursor.execute(fs_sql, (symbol_id, gene_id, feature_id['unattributed']))

    # add feature pub for gene
    cursor.execute(fp_sql, (gene_id, pub_id))
    return gene_name, gene_id


def feature_add_to_allele(cursor, feat_details, allele_id, cvterm_id, org_id, db_id, pub_id, feature_id):
    """Get or create tool.

    If tool_name in feature_id dictionary lookup if it does not exist create it.

    Returns:
        <int> feature_id of the feature.
    """
    new_feat = True
    if feat_details['name'] not in feature_id:
        # create dbxref,  accession -> uniquename
        feat_name = feat_details['name']
        cursor.execute(dbxref_sql, (db_id['FlyBase'], feat_details['uniquename']))
        dbxref_id = cursor.fetchone()[0]
        cursor.execute(feat_sql, (dbxref_id, org_id, feat_details['name'], feat_details['uniquename'],
                       "", 0, cvterm_id[feat_details['type']]))
        feat_id = feature_id[feat_name] = cursor.fetchone()[0]
    else:
        feat_id = feature_id[feat_details['name']]
        new_feat = False

    # add feature pub
    if new_feat:
        try:
            cursor.execute(fp_sql, (feat_id, pub_id))
        except Exception as e:  # it may already exist
            print("Problem {}, just checking".format(e))

    # feature relationship tool and allele
    try:
        cursor.execute(feat_rel_sql, (allele_id, feat_id, cvterm_id['associated_with']))
        feat_rel = cursor.fetchone()[0]
        # feat rel pub
        cursor.execute(frpub_sql, (feat_rel, pub_id))
    except Exception as e:  # should be okay if exists already
        print("Problem {}, just checking".format(e))
    return feat_id


def _create_allele(cursor, allele_name, sgml_name, allele_unique_name, cvterm_id, org_id, db_id, pub_id, feature_id):
    """Create the allele feature."""
    # create dbxref,  accession -> uniquename
    cursor.execute(dbxref_sql, (db_id['FlyBase'], allele_unique_name))
    dbxref_id = cursor.fetchone()[0]

    print("BOB: creating {} {}".format(allele_name, allele_unique_name))
    cursor.execute(feat_sql, (dbxref_id, org_id, allele_name, allele_unique_name, "", 0, cvterm_id['allele']))
    allele_id = cursor.fetchone()[0]

    # add synonym for allele
    cursor.execute(syn_sql, (allele_name, cvterm_id['symbol'], sgml_name))
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym for allele
    if pub_id != feature_id['unattributed']:
        cursor.execute(fs_sql, (symbol_id, allele_id, pub_id))
    cursor.execute(fs_sql, (symbol_id, allele_id, feature_id['unattributed']))

    # add feature pub for allele
    cursor.execute(fp_sql, (allele_id, pub_id))
    return allele_id


def create_allele(cursor, count, gene_id, gene_name, allele_prefix, tool_prefix, cvterm_id, org_id, db_id, pub_id, feature_id):
    """Create allele and link to gene via the ID."""
    global allele_count
    allele_count += 1
    if allele_prefix:
        sgml_name = allele_name = "{}{}".format(allele_prefix, count)
    else:
        tool_name = "{}{}".format(tool_prefix, count+1)
        allele_name = "{}[{}]".format(gene_name, tool_name)
        sgml_name = "{}<up>{}</up>".format(gene_name, tool_name)

    allele_unique_name = 'FB{}{:07d}'.format('al', (allele_count))
    allele_id = _create_allele(cursor, allele_name, sgml_name, allele_unique_name, cvterm_id, org_id, db_id, pub_id, feature_id)

    # feature relationship gene and allele
    cursor.execute(feat_rel_sql, (allele_id, gene_id, cvterm_id['alleleof']))
    feat_rel = cursor.fetchone()[0]

    # feat rel pub
    cursor.execute(frpub_sql, (feat_rel, pub_id))
    return allele_name, allele_id


def create_gene_alleles(cursor, org_dict, feature_id, cvterm_id, db_id, pub_id,
                        num_genes=5, num_alleles=3, gene_prefix=None, allele_prefix=None,
                        tool_prefix=None, tr_format=None, tp_format=None, pub_format=None
                        ):
    """Create the genes and alleles.

    Args:
        num_genes: <int> Number of genes to create add number to end of gene_prefix for names
        num_alleles: <int> Number of alleles to create add number to end of
                   allele_prefix if exists for names OR
                   add [tool_prefix{}] to end of gene name. {} is the allele numbe for that gene
        gene_prefix: <string> gene name prefix to add number on the end of to get gene name.
        allele_prefix: <string> (Optional) If set allele name will be allele name and number
        tool_prefix: <string> (Optional) If set and allele_prefix is not set
                    alelele name => "{}[{}{}]".format(gene_name, tool_prefix, allele_number)
        tr_format: <string> (Optional) If set add transcript for each allele using this name
                   NOTE: 'allele_name' will be replaced with the actual allele name
        tp_format: <string> (Optional) If set add transcript for each allele using this name
                   NOTE: 'tool_name' and 'gene_name' will be replaced with actual tool name and gene names.
        pub_format: <string> (Optional) If set create a new pub for each gene and its subsequent alleles etc.
                   NOTE:{pub_format)_{gene_count} pub will be produced

    Return List: List of genes and their alleles.
       [gene_id1, [allele_id1, allele_id2],
        gene_id2, [allele_id3, allele_id4]]
    """
    global gene_count, allele_count

    org_id = org_dict['Dmel']
    """
    if tool_prefix is given:-
       FBgn0086784 geneprefixX
       FBal0197755 gene_prefixX[toolx]
       FBto0000027 toolx
    """
    gene_allele_list = []
    for i in range(num_genes):
        if pub_format:
            cursor.execute(pub_sql, (cvterm_id['journal'], '{}_{}'.format(pub_format, gene_count), 'FB{}{:07d}'.format('rf', gene_count),
                           '2021', 'mini_{}'.format(gene_count)))
            pub_id = cursor.fetchone()[0]

        (gene_name, gene_id) = create_gene(cursor, i, gene_prefix, cvterm_id, org_id, db_id, pub_id, feature_id)
        print(gene_name)
        allele_ids = []
        # now add 'num_alleles' alleles for each
        for j in range(num_alleles):
            (allele_name, allele_id) = create_allele(cursor, j, gene_id, gene_name, allele_prefix, tool_prefix, cvterm_id, org_id, db_id, pub_id, feature_id)
            create_log = " gene {}: allele {}".format(gene_name, allele_name)
            allele_ids.append(allele_id)
            tool_name = ""
            if tool_prefix:
                tool_name = "{}{}".format(tool_prefix, j+1)
                feat_details = {'name': tool_name,
                                'uniquename': 'FB{}{:07d}'.format('to', (allele_count)),
                                'type': 'engineered_region'}
                feature_add_to_allele(cursor, feat_details, allele_id, cvterm_id, org_id, db_id, pub_id, feature_id)
                create_log += " tool: {}".format(tool_name)
            if tp_format:
                tp_name = tp_format.replace('tool_name', tool_name)
                tp_name = tp_name.replace('gene_name', gene_name)
                feat_details = {'name': tp_name,
                                'uniquename': 'FB{}{:07d}'.format('tp', (allele_count)),
                                'type': 'transgenic_transposable_element'}
                feature_add_to_allele(cursor, feat_details, allele_id, cvterm_id, org_id, db_id, pub_id, feature_id)
                create_log += " tp: {}".format(tp_name)
            if tr_format:
                tr_name = tr_format.replace('allele_name', allele_name)
                feat_details = {'name': tr_name,
                                'uniquename': 'FB{}{:07d}'.format('tr', (allele_count)),
                                'type': 'mRNA'}
                feature_add_to_allele(cursor, feat_details, allele_id, cvterm_id, org_id, db_id, pub_id, feature_id)
                create_log += " tr: {}".format(tr_name)
            print(create_log)
        gene_allele_list.append([gene_id, allele_ids])
    return gene_allele_list
