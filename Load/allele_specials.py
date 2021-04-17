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
from Load.gene_alleles import create_gene_alleles, add_special_merge_data

gene_count = 50000
allele_count = 50000


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


def create_symbols_again(cursor, org_dict, feature_id, cvterm_id, dbxref_id, db_id, pub_id):
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
    """New one with usign generalised functions."""
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


def create_allele_GA90_2(cursor, org_dict, feature_id, cvterm_id, db_id, pub_id):
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
