r"""
:synopsis: Create genes needed for testing.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>

Create the genes needed for testing, For both Dmel and other species.
  Including their :-
  Locations
  Alleles
  Synonyms
  Dbxrefs

Create 50 general genes for each of Dmel, Hsap, Mmus and Zzzz
    So the Dmel gene will look like
      FBgn0000100 -> symbol-1
      FBgn0000200 -> symbol-2
      ...
      FBgn0005000 -> symbol-50

    Other species the name is incremented so:-

    Hsap\symbol-1 -> FBgn0000101, Hsap\symbol-2 -> FBgn0000201 ... Hsap\symbol-50 -> FBgn0005001
    Mmus\symbol-1 -> FBgn0000102
    Zzzz\symbol-1 -> FBgn0000103

Special genes created for specific tests:-
   1) gene with &agr; to check special lookups. 0007_Gene_lookup_check.txt
      FBgn0005100
   2) symbol-10 -> symbol-19 No featureloc to test merging etc

To help know which genes to use for tests try to keep this list up to date.
Genes used in tests that cannot be used again (due to renames or deletions):-
    FBgn0000100 - symbol-1 -> 0003_Gene
"""
from .humanhealth import create_hh, create_hh_dbxref

feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""
fd_sql = """ INSERT INTO feature_dbxref (feature_id, dbxref_id) VALUES (%s, %s) """

gene_sub_count = 0


def create_gene(cursor, organism_name, org_dict, gene_count, cvterm_id, feature_id, pub_id, db_id, add_alpha=False):
    """Create a gene."""
    global gene_sub_count

    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id) VALUES (%s, %s, %s) """
    loc_sql = """ INSERT INTO featureloc (feature_id, srcfeature_id, fmin, fmax, strand) VALUES (%s, %s, %s, %s, %s) """
    fp_sql = """ INSERT INTO feature_pub (feature_id, pub_id) VALUES (%s, %s) """
    fprop_sql = """ INSERT INTO featureprop (feature_id, type_id, value, rank) VALUES (%s, %s, %s, %s) """
    fc_sql = """ INSERT INTO feature_cvterm (feature_id, cvterm_id, pub_id) VALUES (%s, %s, %s) RETURNING feature_cvterm_id """
    fc_dx_sql = """ INSERT INTO feature_cvterm_dbxref (feature_cvterm_id, dbxref_id) VALUES (%s, %s) """
    f_hh_dbxref_sql = """ INSERT INTO feature_humanhealth_dbxref (feature_id, humanhealth_dbxref_id, pub_id) VALUES (%s, %s, %s) """
    fb_code = 'gn'
    grp_sql = """ INSERT INTO grp (name, uniquename, type_id) VALUES (%s, %s, %s) RETURNING grp_id """
    gm_sql = """ INSERT INTO grpmember (type_id, grp_id) VALUES (%s, %s) RETURNING grpmember_id """
    f_gm_sql = """ INSERT INTO feature_grpmember (feature_id, grpmember_id) VALUES (%s, %s) """

    org_id = org_dict[organism_name]
    unique_name = None
    if add_alpha:
        sgml_name = "genechar-α-<up>0002</up>"
        sym_name = "genechar-alpha-[0002]"
        unique_name = 'FB{}{:07d}'.format(fb_code, ((gene_count+1)*100))
    elif organism_name == 'Dmel':
        gene_sub_count = 0
        sgml_name = sym_name = "symbol-{}".format(gene_count+1)
        unique_name = 'FB{}{:07d}'.format(fb_code, ((gene_count+1)*100 + gene_sub_count))
    else:
        gene_sub_count += 1
        sgml_name = sym_name = '{}\\symbol-{}'.format(organism_name, gene_count+1)
        unique_name = 'FB{}{:07d}'.format(fb_code, ((gene_count+1)*100 + gene_sub_count))

    print("Adding gene {} {} for species {} - syn {}".format(unique_name, gene_count+1, organism_name, sym_name))

    # create dbxref,  accession -> uniquename
    cursor.execute(dbxref_sql, (db_id['FlyBase'], unique_name))
    dbxref_id = cursor.fetchone()[0]

    # create the gene feature
    cursor.execute(feat_sql, (dbxref_id, org_id, sym_name, unique_name, "ACTG"*5, 20, cvterm_id['gene']))
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

    # add feature pub
    cursor.execute(fp_sql, (gene_id, pub_id))

    # now add the feature loc
    # make them overlap in sets of 10.
    start = int(gene_count/10)+1
    if start != 2:  # genes 10 -> 19 do  not have loc, as to be megred etc
        cursor.execute(loc_sql, (gene_id, feature_id['2L'], start*100, (start+1)*100, 1))
    elif organism_name == 'Dmel':  # add extra info for merging genes to check.
        # add featureprop
        cursor.execute(fprop_sql, (gene_id, cvterm_id['symbol'], "featprop-{}".format(gene_count+1), 0))

        # add feature_cvterm
        cursor.execute(fc_sql, (gene_id, cvterm_id['protein_coding_gene'], pub_id))
        fc_id = cursor.fetchone()[0]
        cursor.execute(fc_sql, (gene_id, cvterm_id['disease_associated'], pub_id))

        # add feature_cvterm_dbxref
        cursor.execute(dbxref_sql, (db_id['testdb'], 'testdb-{}'.format(gene_count+1)))
        dbxref_id = cursor.fetchone()[0]
        cursor.execute(fc_dx_sql, (fc_id, dbxref_id))

        # feature_grpmember
        cursor.execute(grp_sql, ('grp-{}'.format(gene_count + 1), 'FBgg:temp_{}'.format(gene_count + 1), cvterm_id['gene_group']))
        grp_id = cursor.fetchone()[0]
        cursor.execute(gm_sql, (cvterm_id['grpmember_feature'], grp_id))
        gm_id = cursor.fetchone()[0]
        print("grp {}, grpmem {}".format(grp_id, gm_id))
        cursor.execute(f_gm_sql, (gene_id, gm_id))

        # add feature_humanheath_dbxref
        # get hh, dbxref
        hh_id = create_hh(cursor, feature_id, db_id, org_dict['Hsap'], (gene_count+1)*100 + gene_sub_count, is_obsolete=False)
        cursor.execute(dbxref_sql, (db_id['HGNC'], "HGNC-{}".format((gene_count+1)*100 + gene_sub_count)))
        dbxref_id = cursor.fetchone()[0]
        print("HHID is {}".format(hh_id))
        hh_dbxref_id = create_hh_dbxref(hh_id, dbxref_id, [cvterm_id['hgnc_link']], cursor, pub_id)
        cursor.execute(f_hh_dbxref_sql, (gene_id, hh_dbxref_id, pub_id))

        # add a dbxref to test merges/renames etc
        cursor.execute(dbxref_sql, (db_id['testdb2'], 'testdb2-{}'.format(gene_count+1)))
        dbxref_id = cursor.fetchone()[0]
        cursor.execute(fd_sql, (gene_id, dbxref_id))

        # feature interaction not needed, only one in chado for gene features

    return gene_id


def add_gene_data(cursor, organism_id, feature_id, cvterm_id, dbxref_id, pub_id, db_id):
    """Add all the genes needed for testing."""
    feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id) VALUES (%s, %s, %s) RETURNING feature_relationship_id """
    alleles = []

    for i in range(50):
        feature_id['gene'] = gene_id = create_gene(cursor, 'Dmel', organism_id, i, cvterm_id, feature_id, pub_id, db_id)

        # create mouse and human genes
        create_gene(cursor, 'Hsap', organism_id, i, cvterm_id, feature_id, pub_id, db_id)
        create_gene(cursor, 'Mmus', organism_id, i, cvterm_id, feature_id, pub_id, db_id)
        create_gene(cursor, 'Zzzz', organism_id, i, cvterm_id, feature_id, pub_id, db_id)

        # add allele for each gene and add feature_relationship
        cursor.execute(feat_sql, (None, organism_id['Dmel'], "al-symbol-{}".format(i+1),
                       'FBal:temp_{}'.format(i), None, 200, cvterm_id['gene']))
        feature_id["al-symbol-{}".format(i+1)] = allele_id = cursor.fetchone()[0]
        alleles.append(allele_id)
        cursor.execute(feat_rel_sql, (allele_id, gene_id, cvterm_id['alleleof']))

        # add ClinVar dbxrefs to allele for testing changing description and removal
        for j in range(5):
            cursor.execute(fd_sql, (allele_id, dbxref_id['ClinVar{}'.format(j+1)]))

    # add gene with &agr; to check special lookups. 0007_Gene_lookup_check.txt
    feature_id['gene'] = gene_id = create_gene(cursor, 'Dmel', organism_id, i+1, cvterm_id, feature_id, pub_id, db_id, add_alpha=True)
    return
