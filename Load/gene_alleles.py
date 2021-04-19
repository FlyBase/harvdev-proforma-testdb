r"""
:synopsis: Create genes and alleles needed for testing.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>

Create the genes needed for testing, For both Dmel and other species.
  Including their :-
  Locations
  Alleles
  Synonyms
  Dbxrefs

Create 50 general genes for each of Dmel, and 10 for Hsap, Mmus and Zzzz
    So the Dmel gene will look like
      FBgn0000001 -> symbol-1
      FBgn0000002 -> symbol-2
      ...
      FBgn0000050 -> symbol-50

    Other species the name is incremented so (10 of each):-

    Hsap\symbol-1 -> FBgn0000051, Hsap\symbol-2 -> FBgn0000052 ... Hsap\symbol-10 -> FBgn0000070
    Zzzz\symbol-1 -> FBal0000061
    Mmus\symbol-1 -> FBgn0000071

Special genes created for specific tests:-
   1) gene with &agr; to check special lookups. 0007_Gene_lookup_check.txt
      FBgn0005100
   2) symbol-10 -> symbol-19 No featureloc to test merging etc

To help know which genes to use for tests try to keep this list up to date.
Genes used in tests that cannot be used again (due to renames or deletions):-
    FBgn0000100 - symbol-1 -> 0003_Gene
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
from .humanhealth import create_hh, create_hh_dbxref

gene_count = 0
allele_count = 0
hh_count = 1000

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

# extra for merging genes
fc_sql = """ INSERT INTO feature_cvterm (feature_id, cvterm_id, pub_id) VALUES (%s, %s, %s) RETURNING feature_cvterm_id """
fcp_sql = """ INSERT INTO feature_cvtermprop (feature_cvterm_id, type_id, value, rank) VALUES (%s, %s, %s, %s) """
fc_dx_sql = """ INSERT INTO feature_cvterm_dbxref (feature_cvterm_id, dbxref_id) VALUES (%s, %s) """
f_hh_dbxref_sql = """ INSERT INTO feature_humanhealth_dbxref (feature_id, humanhealth_dbxref_id, pub_id) VALUES (%s, %s, %s) """
fb_code = 'gn'
grp_sql = """ INSERT INTO grp (name, uniquename, type_id) VALUES (%s, %s, %s) RETURNING grp_id """
gm_sql = """ INSERT INTO grpmember (type_id, grp_id) VALUES (%s, %s) RETURNING grpmember_id """
f_gm_sql = """ INSERT INTO feature_grpmember (feature_id, grpmember_id) VALUES (%s, %s) """
fd_sql = """ INSERT INTO feature_dbxref (feature_id, dbxref_id) VALUES (%s, %s) """
loc_sql = """ INSERT INTO featureloc (feature_id, srcfeature_id, fmin, fmax, strand) VALUES (%s, %s, %s, %s, %s) """


def add_special_merge_data(cursor, feature_id, cvterm_id, pub_id, dbxref_id, db_id, org_dict):
    """Add data needed to test merging of genes."""
    global hh_count
    for i in range(11, 20):
        gene_id = feature_id['symbol-{}'.format(i)]
        print("merge data for symbols {}".format(i))
        # add featureprop
        cursor.execute(fprop_sql, (gene_id, cvterm_id['symbol'], "featprop-{}".format(i), 0))

        # add feature_cvterm
        cursor.execute(fc_sql, (gene_id, cvterm_id['protein_coding_gene'], pub_id))
        fc_id = cursor.fetchone()[0]
        cursor.execute(fcp_sql, (fc_id, cvterm_id['gene_class'], None, 0))  # add prop for gene class
        cursor.execute(fc_sql, (gene_id, cvterm_id['disease_associated'], pub_id))

        # add feature_cvterm_dbxref
        cursor.execute(dbxref_sql, (db_id['testdb'], 'testdb-{}'.format(i)))
        dbxref_id['testdb-{}'.format(i)] = cursor.fetchone()[0]
        cursor.execute(fc_dx_sql, (fc_id, dbxref_id['testdb-{}'.format(i)]))

        # feature_grpmember
        cursor.execute(grp_sql, ('grp-{}'.format(i), 'FBgg:temp_{}'.format(i), cvterm_id['gene_group']))
        grp_id = cursor.fetchone()[0]
        cursor.execute(gm_sql, (cvterm_id['grpmember_feature'], grp_id))
        gm_id = cursor.fetchone()[0]
        print("grp {}, grpmem {}".format(grp_id, gm_id))
        cursor.execute(f_gm_sql, (gene_id, gm_id))

        # add feature_humanheath_dbxref
        # get hh, dbxref
        hh_id = create_hh(cursor, feature_id, db_id, org_dict['Hsap'], hh_count, is_obsolete=False)
        cursor.execute(dbxref_sql, (db_id['HGNC'], "HGNC-{}".format(hh_count)))

        dbxref_id["HGNC-{}".format(hh_count)] = cursor.fetchone()[0]
        print("HHID is {}".format(hh_id))
        hh_dbxref_id = create_hh_dbxref(hh_id, dbxref_id["HGNC-{}".format(hh_count)], [cvterm_id['hgnc_link']], cursor, pub_id)
        cursor.execute(f_hh_dbxref_sql, (gene_id, hh_dbxref_id, pub_id))
        hh_count += 1

        # add a dbxref to test merges/renames etc
        cursor.execute(dbxref_sql, (db_id['testdb2'], 'testdb2-{}'.format(i)))
        dbxref_id['testdb2-{}'.format(i)] = cursor.fetchone()[0]
        cursor.execute(fd_sql, (gene_id, dbxref_id['testdb2-{}'.format(i)]))

    for i in range(22, 24):  # and feature location to symbol-22 and symbol-23, to tes they cannot merge with location
        cursor.execute(loc_sql, (feature_id["symbol-{}".format(i)], feature_id['2L'], i*100, (i+1)*100, 1))

    # al-symbol-3
    for i in range(5):  # five VarClin1->ClinVar5
        cursor.execute(fd_sql, (feature_id["al-symbol-3"], dbxref_id['ClinVar{}'.format(i+1)]))

    # make gene part of gene_group for subset
    for i in range(40, 50):
        cursor.execute(fc_sql, (feature_id["symbol-{}".format(i)], cvterm_id['gene_group'], pub_id))


def create_gene(cursor, count, gene_prefix, cvterm_id, org_id, db_id, pub_id, feature_id):
    """Get gene name."""
    global gene_count
    gene_count += 1
    gene_name = "{}{}".format(gene_prefix, count+1)
    gene_unique_name = 'FB{}{:07d}'.format('gn', (gene_count))
    gene_sgml_name = gene_name.replace('alpha', 'α')

    # create dbxref,  accession -> uniquename
    cursor.execute(dbxref_sql, (db_id['FlyBase'], gene_unique_name))
    dbxref_id = cursor.fetchone()[0]

    # create the gene feature
    cursor.execute(feat_sql, (dbxref_id, org_id, gene_name, gene_unique_name, "ACTG"*5, 20, cvterm_id['gene']))
    gene_id = feature_id[gene_name] = cursor.fetchone()[0]

    for syn_type in ('symbol', 'fullname'):
        # add synonym for gene
        cursor.execute(syn_sql, (gene_name, cvterm_id[syn_type], gene_sgml_name))
        symbol_id = cursor.fetchone()[0]

        # add feature_synonym for gene
        if pub_id != feature_id['unattributed']:
            cursor.execute(fs_sql, (symbol_id, gene_id, pub_id))
        cursor.execute(fs_sql, (symbol_id, gene_id, feature_id['unattributed']))

    # add feature pub for gene
    cursor.execute(fp_sql, (gene_id, pub_id))
    return gene_name, gene_id


def feature_add_to_allele(cursor, count, feat_details, tool_name, gene_name, allele_name,
                          allele_id, cvterm_id, org_id, db_id, pub_id, feature_id):
    """Get or create tool.

    If tool_name in feature_id dictionary lookup if it does not exist create it.

    Returns:
        <int> feature_id of the feature.
    """
    global allele_count
    new_feat = True
    name = feat_details['name'].replace('<count>', str(count+1))
    name = name.replace('<gene_name>', gene_name)
    name = name.replace('<tool_name>', "{}{}".format(tool_name, count+1))
    name = name.replace('<allele_name>', allele_name)
    uniquename = feat_details['uniquename'].replace('<number>', "{:07d}".format(allele_count))
    if name not in feature_id:
        # create dbxref,  accession -> uniquename
        cursor.execute(dbxref_sql, (db_id['FlyBase'], uniquename))
        dbxref_id = cursor.fetchone()[0]
        cursor.execute(feat_sql, (dbxref_id, org_id, name, uniquename,
                       "", 0, cvterm_id[feat_details['type']]))
        feat_id = feature_id[name] = cursor.fetchone()[0]

        # add synonyms
        cursor.execute(syn_sql, (name, cvterm_id['symbol'], name))
        symbol_id = cursor.fetchone()[0]

        # add feature_synonym
        cursor.execute(fs_sql, (symbol_id, feat_id, pub_id))

    else:
        feat_id = feature_id[name]
        new_feat = False

    # add feature pub
    if new_feat:
        try:
            cursor.execute(fp_sql, (feat_id, pub_id))
        except Exception as e:  # it may already exist
            print("Problem {}, just checking".format(e))

    subject_id = allele_id
    object_id = feat_id
    if 'subject' in feat_details and feat_details['subject']:
        object_id = allele_id
        subject_id = feat_id
    # feature relationship tool and allele
    try:
        cursor.execute(feat_rel_sql, (subject_id, object_id, cvterm_id[feat_details['relationship']]))
        feat_rel = cursor.fetchone()[0]
        # feat rel pub
        cursor.execute(frpub_sql, (feat_rel, pub_id))
    except Exception as e:  # should be okay if exists already
        print("Problem {}, just checking".format(e))
    return "{}: {}".format(feat_details['type'], name)


def _create_allele(cursor, allele_name, sgml_name, allele_unique_name, cvterm_id, org_id, db_id, pub_id, feature_id):
    """Create the allele feature."""
    # create dbxref,  accession -> uniquename
    cursor.execute(dbxref_sql, (db_id['FlyBase'], allele_unique_name))
    dbxref_id = cursor.fetchone()[0]

    cursor.execute(feat_sql, (dbxref_id, org_id, allele_name, allele_unique_name, "", 0, cvterm_id['allele']))
    allele_id = feature_id[allele_name] = cursor.fetchone()[0]

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


def create_allele(cursor, gene_num, allele_num, gene_id, gene_name, allele_prefix, tool_prefix, cvterm_id, org_id, db_id, pub_id, feature_id):
    """Create allele and link to gene via the ID."""
    global allele_count
    allele_count += 1
    if allele_prefix:
        sgml_name = allele_name = "{}{}".format(allele_prefix, gene_num+1)
    else:
        tool_name = "{}{}".format(tool_prefix, allele_num+1)
        allele_name = "{}[{}]".format(gene_name, tool_name)
        sgml_name = "{}<up>{}</up>".format(gene_name, tool_name)
        sgml_name = sgml_name.replace('alpha', 'α')

    allele_unique_name = 'FB{}{:07d}'.format('al', (allele_count))
    allele_id = _create_allele(cursor, allele_name, sgml_name, allele_unique_name, cvterm_id, org_id, db_id, pub_id, feature_id)

    # feature relationship gene and allele
    cursor.execute(feat_rel_sql, (allele_id, gene_id, cvterm_id['alleleof']))
    feat_rel = cursor.fetchone()[0]

    # feat rel pub
    cursor.execute(frpub_sql, (feat_rel, pub_id))
    return allele_name, allele_id


def add_props(cursor, feat_id, feat_props, cvterm_id, pub_id):
    """Add props to feature.

    feat_id: <int> feature_id to have props added to it.
    feat_prop: <dict> prop cvterm and value
        i.e. props = {'GA12a': ['aminoacid_rep', r'Amino acid replacement: Q100{}term prop 12a'],
                     'GA12a-2': ['nucleotide_sub', r'Nucleotide substitution: {}']}
    """
    for item in feat_props.values():
        if item[1]:
            value = item[1].format(allele_count)
        else:
            value = item[1]
        cursor.execute(fprop_sql, (feat_id, cvterm_id[item[0]], value, 0))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fpp_sql, (fp_id, pub_id))


def create_gene_alleles(cursor, org_dict, feature_id, cvterm_id, db_id, pub_id,
                        num_genes=5, num_alleles=3, gene_prefix=None, allele_prefix=None,
                        tool_prefix=None, gene_relationships=None, allele_relationships=None, pub_format=None,
                        gene_props=None, allele_props=None, org_abbr='Dmel'
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
        gene_relationships: <dict> relationships to add to each gene.
        allele_relationships: <dict> relationships to add to each allele.
        tr_format: <string> (Optional) If set add transcript for each allele using this name
                   NOTE: 'allele_name' will be replaced with the actual allele name
        tp_format: <string> (Optional) If set add transcript for each allele using this name
                   NOTE: 'tool_name' and 'gene_name' will be replaced with actual tool name and gene names.
        pub_format: <string> (Optional) If set create a new pub for each gene and its subsequent alleles etc.
                   NOTE:{pub_format)_{gene_count} pub will be produced
        gene_props: <dict> props to be added to each gene. dict has a field: [proptype, value] format
        alelele_props: <dict>props to be added to each allele. dict has a field: [proptype, value] format
        org_abbr: <string> (default 'Dmel') abbreviation for the organism.

    Return List: List of genes and their alleles.
       [gene_id1, [allele_id1, allele_id2],
        gene_id2, [allele_id3, allele_id4]]
    """
    global gene_count, allele_count

    org_id = org_dict[org_abbr]
    """
    if tool_prefix is given:-
       FBgn0086784 geneprefixX
       FBal0197755 gene_prefixX[toolx]
       FBto0000027 toolx
    """
    if tool_prefix and allele_relationships:
        allele_relationships.append({'name': "{}<count>".format(tool_prefix),
                                     'uniquename': 'FBto<number>',
                                     'type': 'engineered_region',
                                     'relationship': 'associated_with'})
    gene_allele_list = []
    for i in range(num_genes):
        if pub_format:
            pub_name = '{}{}'.format(pub_format, i+1)
            cursor.execute(pub_sql, (cvterm_id['journal'], pub_name, 'FB{}{:07d}'.format('rf', gene_count),
                           '2021', 'mini_{}'.format(i+1)))
            pub_id = feature_id[pub_name] = cursor.fetchone()[0]

        (gene_name, gene_id) = create_gene(cursor, i, gene_prefix, cvterm_id, org_id, db_id, pub_id, feature_id)
        create_log = " gene: {}".format(gene_name)
        if gene_relationships:
            for item in gene_relationships:
                mess = feature_add_to_allele(cursor, i, item, tool_prefix, gene_name, "", gene_id, cvterm_id, org_id, db_id, pub_id, feature_id)
                create_log = " {}".format(mess)
        print(gene_name)
        allele_ids = []
        # now add 'num_alleles' alleles for each
        for j in range(num_alleles):
            (allele_name, allele_id) = create_allele(cursor, i, j, gene_id, gene_name, allele_prefix, tool_prefix, cvterm_id, org_id, db_id, pub_id, feature_id)
            create_log += " allele: {}".format(allele_name)
            allele_ids.append(allele_id)
            if allele_relationships:
                for item in allele_relationships:
                    rela_pub = pub_id
                    if 'relationship_pub' in item:
                        print("NOTICE: using pub {} for {}.".format(item['relationship_pub'], item['name']))
                        rela_pub = feature_id[item['relationship_pub']]
                    mess = feature_add_to_allele(cursor, j, item, tool_prefix, gene_name, allele_name, allele_id,
                                                 cvterm_id, org_id, db_id, rela_pub, feature_id)
                    create_log += " {}".format(mess)
            print(create_log)
            # add props if defined to allele
            if allele_props:
                add_props(cursor, allele_id, allele_props, cvterm_id, pub_id)
        if gene_props:
            add_props(cursor, gene_id, gene_props, cvterm_id, pub_id)
        gene_allele_list.append([gene_id, allele_ids])
    return gene_allele_list


def create_alpha_alleles(cursor, org_dict, feature_id, cvterm_id, db_id, pub_id):
    """Create genes and alleles with 'alpha' in them.

    NOTE: alpha is substituted to 'α' in synonym_sgml in the create_gene_alleles function.
    """
    create_gene_alleles(
        cursor, org_dict, feature_id, cvterm_id, db_id, pub_id,
        num_genes=1,
        num_alleles=1,
        tool_prefix='Clk',
        gene_prefix='gene_with_alpha',
        )


def add_gene_G24(cursor, organism_id, feature_id, cvterm_id, dbxref_id, pub_id, db_id):
    """Add data to test G24 banc and bangd operations."""
    create_gene_alleles(
        cursor, organism_id, feature_id, cvterm_id, db_id, pub_id,
        num_genes=10,
        num_alleles=1,
        gene_prefix='G24gene',
        allele_prefix=None,
        tool_prefix='Clk',
        pub_format="G24_title_"
        )
    # G24 data. feature cvterm props
    fc_sql = """ INSERT INTO feature_cvterm (feature_id, cvterm_id, pub_id) VALUES (%s, %s, %s) RETURNING feature_cvterm_id """
    fcp_sql = """ INSERT INTO feature_cvtermprop (feature_cvterm_id, type_id, value, rank) VALUES (%s, %s, %s, %s) """
    data = [
        {'cvterm': 'date', 'cvname': 'feature_cvtermprop type', 'value': '19671008'},
        {'cvterm': 'provenance', 'cvname': 'FlyBase miscellaneous CV', 'value': 'FlyBase'},
        {'cvterm': 'evidence_code', 'cvname': 'FlyBase miscellaneous CV', 'value': 'inferred from direct assay'},
        {'cvterm': 'located_in', 'cvname': 'relationship', 'value': None}]

    for i in range(10):
        # create feature cvterm
        cursor.execute(fc_sql, (feature_id['G24gene{}'.format(i+1)], cvterm_id['extracellular space'], pub_id))
        fc_id = cursor.fetchone()[0]

        # create feature cvterm props
        for item in data:
            cursor.execute(fcp_sql, (fc_id, cvterm_id[item['cvterm']], item['value'], 0))


def create_symbols(cursor, org_dict, feature_id, cvterm_id, dbxref_id, db_id, pub_id):
    """Create the basic symbols.

    NOTE: Probably should have chnaged these to reflect proper genes and alleles but far too late now.
    """
    create_gene_alleles(
        cursor, org_dict, feature_id, cvterm_id, db_id, pub_id,
        num_genes=50,
        num_alleles=1,
        gene_prefix='symbol-',
        allele_prefix='al-symbol-',
        )

    add_special_merge_data(cursor, feature_id, cvterm_id, pub_id, dbxref_id, db_id, org_dict)  # For symbols 11 -> 19

    for abbr in ('Hsap', 'Zzzz', 'Mmus'):
        create_gene_alleles(
            cursor, org_dict, feature_id, cvterm_id, db_id, pub_id,
            num_genes=10,
            num_alleles=1,
            org_abbr=abbr,
            gene_prefix='{}\\symbol-'.format(abbr),
            allele_prefix='{}\\al-symbol-'.format(abbr),
            )


def create_merge_allele(cursor, org_dict, feature_id, cvterm_id, db_id, pub_id):
    """Create gene and alles for merging."""
    allele_relationships = [{'name': 'P{<tool_name>-<gene_name>.H}',
                             'uniquename': 'FBtp<number>',
                             'type': 'transgenic_transposable_element',
                             'relationship': 'associated_with'},
                            {'name': '<allele_name>[ZR]',
                             'uniquename': 'FBtr<number>',
                             'type': 'mRNA',
                             'relationship': 'associated_with',
                             'subject': True,
                             'relationship_pub': 'unattributed'}
                            ]
    gene_alleles = create_gene_alleles(
                        cursor, org_dict, feature_id, cvterm_id, db_id, pub_id,
                        num_genes=5,
                        num_alleles=3,
                        gene_prefix='merge_gene',
                        allele_prefix=None,
                        tool_prefix='Clk',
                        allele_relationships=allele_relationships,
                        pub_format="merge_title_"
                        )
    for g_a in gene_alleles:
        print("gene {}".format(g_a[0]))


def create_gene_allele_for_GA10(cursor, org_dict, feature_id, cvterm_id, db_id, pub_id):
    """Test data for GA10."""
    allele_relationships = [{'name': 'P{<tool_name>-<gene_name>.H}',
                             'uniquename': 'FBtp<number>',
                             'type': 'transgenic_transposable_element',
                             'relationship': 'associated_with'}]
    create_gene_alleles(cursor, org_dict, feature_id, cvterm_id, db_id, pub_id,
                        num_genes=5,
                        num_alleles=3,
                        gene_prefix='GA10gene',
                        allele_prefix=None,
                        tool_prefix='GA10Tool',
                        allele_relationships=allele_relationships,
                        pub_format="GA10_title_"
                        )


def create_gene_alleles_with_props(cursor, org_dict, feature_id, cvterm_id, db_id, pub_id):
    """New one with using generalised functions."""
    props = {'GA12a': ['aminoacid_rep', r'Amino acid replacement: Q100{}term prop 12a'],
             'GA12a-2': ['nucleotide_sub', r'Nucleotide substitution: {}'],
             'GA12b': ['molecular_info', r'@Tool-sym-{}@ some test prop wrt 12b'],
             'GA30f': ['propagate_transgenic_uses', None],
             'GA85': ['deliberate_omission', 'default comment'],
             'GA36': ['disease_associated', None]}

    gene_alleles = create_gene_alleles(
                        cursor, org_dict, feature_id, cvterm_id, db_id, pub_id,
                        num_genes=5,
                        num_alleles=1,
                        gene_prefix='geneprop',
                        allele_prefix=None,
                        tool_prefix='Clk',
                        allele_props=props
                        )
    for g_a in gene_alleles:
        print("gene {}".format(g_a[0]))


def create_allele_GA90(cursor, org_dict, feature_id, cvterm_id, db_id, pub_id):
    feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""
    # fd_sql = """ INSERT INTO feature_dbxref (feature_id, dbxref_id) VALUES (%s, %s) """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id) VALUES (%s, %s, %s) """
    feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id)
                       VALUES (%s, %s, %s) RETURNING feature_relationship_id """
    frpub_sql = """ INSERT INTO feature_relationship_pub (feature_relationship_id, pub_id) VALUES (%s, %s) """
    fp_sql = """ INSERT INTO feature_pub (feature_id, pub_id) VALUES (%s, %s) """
    fprop_sql = """ INSERT INTO featureprop (feature_id, type_id, value, rank) VALUES (%s, %s, %s, %s) RETURNING featureprop_id """
    fpp_sql = """ INSERT INTO featureprop_pub (featureprop_id, pub_id) VALUES (%s, %s) """
    loc_sql = """ INSERT INTO featureloc (feature_id, srcfeature_id, fmin, fmax, strand) VALUES (%s, %s, %s, %s, %s) """
    allele_relationships = [{'name': '',
                             'uniquename': 'FBtp<number>',
                             'type': 'transgenic_transposable_element',
                             'relationship': 'associated_with'}]
    create_gene_alleles(cursor, org_dict, feature_id, cvterm_id, db_id, pub_id,
                        num_genes=3,
                        num_alleles=1,
                        gene_prefix='GA90_',
                        allele_prefix=None,
                        tool_prefix='',
                        allele_relationships=allele_relationships,
                        pub_format="GA90_title_"
                        )
    for i in range(3):
        allele_name = "GA90_{}[1]".format(i+1)
        org_id = org_dict['Dmel']
        symbol_id = feature_id[allele_name]
        pub_id = feature_id['GA90_title_{}'.format(i+1)]
        ##################################
        # create point mutation for allele NOTE: pm has same name as allele
        ##################################
        cursor.execute(feat_sql, (None, org_id, allele_name, allele_name, "", 0, cvterm_id['point_mutation']))
        pm_id = cursor.fetchone()[0]

        # # add synonym for point_mutation: ALREADY EXISTS
        # cursor.execute(syn_sql, (allele_name, cvterm_id['symbol'], sgml_name))
        # pm_symbol_id = cursor.fetchone()[0]

        # add feature_synonym for point_mutation
        if pub_id != feature_id['unattributed']:
            cursor.execute(fs_sql, (symbol_id, pm_id, pub_id))
        cursor.execute(fs_sql, (symbol_id, pm_id, feature_id['unattributed']))

        # add feature pub for point_mutation
        cursor.execute(fp_sql, (pm_id, pub_id))

        # feature relationship allele and point_mutation
        print("\t allele {}: point_mutation {}".format(allele_name, allele_name))
        cursor.execute(feat_rel_sql, (pm_id, feature_id[allele_name], cvterm_id['partof']))
        feat_rel = cursor.fetchone()[0]
        cursor.execute(frpub_sql, (feat_rel, pub_id))

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


def add_gene_data_for_bang(cursor, organism_id, feature_id, cvterm_id, dbxref_id, pub_id, db_id):
    """Add all the genes needed for testing.

    Separate as has to be done last when everyrthing exists.
    """
    fr_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id) VALUES (%s, %s, %s) RETURNING feature_relationship_id """
    frp_sql = """ INSERT INTO feature_relationshipprop (feature_relationship_id, type_id, value, rank) VALUES (%s, %s, %s, %s) """
    frpub_sql = """ INSERT INTO feature_relationship_pub (feature_relationship_id, pub_id) VALUES (%s, %s) """
    fc_sql = """ INSERT INTO feature_cvterm (feature_id, cvterm_id, pub_id) VALUES (%s, %s, %s) RETURNING feature_cvterm_id """
    fcp_sql = """ INSERT INTO feature_cvtermprop (feature_cvterm_id, type_id, value, rank) VALUES (%s, %s, %s, %s) """
    fp_sql = """ INSERT INTO featureprop (feature_id, type_id, value, rank) VALUES (%s, %s, %s, %s) RETURNING featureprop_id """
    fpp_sql = """ INSERT INTO featureprop_pub (featureprop_id, pub_id) VALUES (%s, %s) """

    # single values/One empty
    for i in range(40, 45):
        count = 0

        # G30
        cursor.execute(fc_sql, (feature_id['symbol-{}'.format(i)], cvterm_id['ncRNA_gene'], pub_id))
        fc_id = cursor.fetchone()[0]
        cursor.execute(fcp_sql, (fc_id, cvterm_id['gene_class'], None, count))

        # G10 bands feature relationship(prop)
        for cvterm_name in ['cyto_left_end', 'cyto_right_end']:
            # G10a Bands (frp)
            cursor.execute(fr_sql, (feature_id['symbol-{}'.format(i)],
                                    feature_id['band-{}A1'.format(94+count)],
                                    cvterm_id[cvterm_name]))
            fr_id = cursor.fetchone()[0]
            cursor.execute(frp_sql, (fr_id, cvterm_id[cvterm_name], '(determined by in situ hybridisation)', 0))
            cursor.execute(frpub_sql, (fr_id, pub_id))

            # G10b Band (fr) no prop
            cursor.execute(fr_sql, (feature_id['symbol-{}'.format(i)],
                                    feature_id['band-{}B1'.format(95+count)],
                                    cvterm_id[cvterm_name]))
            fr_id = cursor.fetchone()[0]
            cursor.execute(frpub_sql, (fr_id, pub_id))

        # G7b feature relationship
        tool_sym = "P{}TE{}{}".format('{', count+1, '}')
        cursor.execute(fr_sql, (feature_id['symbol-{}'.format(i)], feature_id[tool_sym], cvterm_id['recom_right_end']))
        fr_id = cursor.fetchone()[0]
        cursor.execute(frpub_sql, (fr_id, pub_id))

        # G11 Feature prop
        cursor.execute(fp_sql, (feature_id['symbol-{}'.format(i)], cvterm_id['cyto_loc_comment'], 'somevalue', 0))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fpp_sql, (fp_id, pub_id))

    # multiple values
    for i in range(45, 51):
        count = 0

        # G30 Add 2.
        cursor.execute(fc_sql, (feature_id['symbol-{}'.format(i)], cvterm_id['ncRNA_gene'], pub_id))
        fc_id = cursor.fetchone()[0]
        cursor.execute(fcp_sql, (fc_id, cvterm_id['gene_class'], None, count))

        cursor.execute(fc_sql, (feature_id['symbol-{}'.format(i)], cvterm_id['mRNA'], pub_id))
        fc_id = cursor.fetchone()[0]
        cursor.execute(fcp_sql, (fc_id, cvterm_id['gene_class'], None, count))

        # G10 bands feature relationship(prop)
        for bit in 'ABCD':
            for cvterm_name in ['cyto_left_end', 'cyto_right_end']:
                # G10a Bands (frp)
                cursor.execute(fr_sql, (feature_id['symbol-{}'.format(i)],
                                        feature_id['band-{}{}1'.format(94+count, bit)],
                                        cvterm_id[cvterm_name]))
                fr_id = cursor.fetchone()[0]
                cursor.execute(frp_sql, (fr_id, cvterm_id[cvterm_name], '(determined by in situ hybridisation)', 0))
                cursor.execute(frpub_sql, (fr_id, pub_id))

                # G10b Band (fr) no prop
                cursor.execute(fr_sql, (feature_id['symbol-{}'.format(i)],
                                        feature_id['band-{}{}2'.format(95+count, bit)],
                                        cvterm_id[cvterm_name]))
                fr_id = cursor.fetchone()[0]
                cursor.execute(frpub_sql, (fr_id, pub_id))

        # G7b feature relationship
        tool_sym = "P{}TE{}{}".format('{', count+1, '}')
        cursor.execute(fr_sql, (feature_id['symbol-{}'.format(i)], feature_id[tool_sym], cvterm_id['recom_right_end']))
        fr_id = cursor.fetchone()[0]
        cursor.execute(frpub_sql, (fr_id, pub_id))

        tool_sym = "P{}TE{}{}".format('{', count+2, '}')
        cursor.execute(fr_sql, (feature_id['symbol-{}'.format(i)], feature_id[tool_sym], cvterm_id['recom_right_end']))
        fr_id = cursor.fetchone()[0]
        cursor.execute(frpub_sql, (fr_id, pub_id))

        # G11 Feature prop
        cursor.execute(fp_sql, (feature_id['symbol-{}'.format(i)], cvterm_id['cyto_loc_comment'], 'somevalue', 0))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fpp_sql, (fp_id, pub_id))

        cursor.execute(fp_sql, (feature_id['symbol-{}'.format(i)], cvterm_id['cyto_loc_comment'], 'anothervalue', 1))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fpp_sql, (fp_id, pub_id))


def add_genes_and_alleles(cursor, organism_id, feature_id, cvterm_id, dbxref_id, db_id, pub_id):
    """Create genes and alleles needed for testing."""
    # add_gene_data(cursor, organism_id, feature_id, cvterm_id, dbxref_id, pub_id, db_id)
    create_symbols(cursor, organism_id, feature_id, cvterm_id, dbxref_id, db_id, pub_id)

    add_gene_data_for_bang(cursor, organism_id, feature_id, cvterm_id, dbxref_id, pub_id, db_id)

    create_merge_allele(cursor, organism_id, feature_id, cvterm_id, db_id, feature_id['unattributed'])

    create_allele_GA90(cursor, organism_id, feature_id, cvterm_id, db_id, feature_id['unattributed'])

    create_gene_allele_for_GA10(cursor, organism_id, feature_id, cvterm_id, db_id, feature_id['unattributed'])

    # now done in add_gene_data_for_bang
    add_gene_G24(cursor, organism_id, feature_id, cvterm_id, dbxref_id, pub_id, db_id)

    create_gene_alleles_with_props(cursor, organism_id, feature_id, cvterm_id, db_id, feature_id['Nature_2'])
    create_alpha_alleles(cursor, organism_id, feature_id, cvterm_id, db_id, feature_id['Nature_3'])
