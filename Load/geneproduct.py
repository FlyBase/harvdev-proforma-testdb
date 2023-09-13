r"""
:synopsis: Create genes and alleles etc needed for testing of geneproducts.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>


create 30 genes for testing geneproducts.

first ten only linked to alleles
fb_test=# select f.name, f.uniquename, cvt.name from feature f, cvterm cvt where f.type_id = cvt.cvterm_id and f.name like 'gpt5%';
    name    | uniquename  |  name
------------+-------------+--------
 gpt5       | FBgn0000126 | gene
 gpt5[Clk1] | FBal0000165 | allele
 gpt5[Clk2] | FBal0000166 | allele

second 10 also linked to mRNA
fb_test=# select f.name, f.uniquename, cvt.name from feature f, cvterm cvt where f.type_id = cvt.cvterm_id and f.name like 'gpt15%';
    name     | uniquename  |  name
-------------+-------------+--------
 gpt15       | FBgn0000136 | gene
 gpt15-RA    | FBtr0000106 | mRNA
 gpt15-RB    | FBtr0000107 | mRNA
 gpt15[Clk1] | FBal0000185 | allele
 gpt15[Clk2] | FBal0000186 | allele

last 10 linked to mRNA and polypeptides
fb_test=# select f.name, f.uniquename, cvt.name from feature f, cvterm cvt where f.type_id = cvt.cvterm_id and f.name like 'gpt25%';
    name     | uniquename  |    name
-------------+-------------+-------------
 gpt25       | FBgn0000146 | gene
 gpt25-RA    | FBtr0000126 | mRNA
 gpt25-RB    | FBtr0000127 | mRNA
 gpt25[Clk1] | FBal0000205 | allele
 gpt25[Clk2] | FBal0000206 | allele
 gpt25-PB    | FBpp0000027 | polypeptide
 gpt25-PA    | FBpp0000026 | polypeptide
"""
from .gene_alleles import create_gene_alleles

feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""
fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id, is_current) VALUES (%s, %s, %s, %s) """
syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id)
                   VALUES (%s, %s, %s) RETURNING feature_relationship_id """


def create_geneproducts(cursor, organism_id, feature_id, cvterm_id, dbxref_id, db_id, pub_id):

    create_gene_alleles(
        cursor, organism_id, feature_id, cvterm_id, db_id, pub_id,
        num_genes=30,
        num_alleles=2,
        gene_prefix='gpt',
        allele_prefix=None,
        tool_prefix='Clk'
    )

    # first 10 genes have alleles only.
    for gene_count in range(10, 30):
        # 10 ->29 have transcripts (mRNA)
        # gptx-Ry x=gene_count y='A', 'B';
        gene_name = f"gpt{gene_count}"
        for postfix in ['A', 'B']:
            tr_name = f"{gene_name}-R{postfix}"
            cursor.execute(feat_sql, (None, organism_id['Dmel'], tr_name,
                                      'FBtr:temp_0', None, None, cvterm_id['mRNA']))
            feature_id[tr_name] = mrna_id = cursor.fetchone()[0]

            # add synonyms
            cursor.execute(syn_sql, (tr_name, cvterm_id['symbol'], tr_name))
            symbol_id = cursor.fetchone()[0]

            # add feature_synonym
            cursor.execute(fs_sql, (symbol_id, mrna_id, pub_id, True))

            # add relationship to gene
            cursor.execute(feat_rel_sql, (feature_id[tr_name], feature_id[gene_name], cvterm_id['partof']))

        # 20 -> 29 have polypeptides too.
        if gene_count < 20:
            continue
        for postfix in ['A', 'B']:
            pp_name = f"{gene_name}-P{postfix}"
            cursor.execute(feat_sql, (None, organism_id['Dmel'], pp_name,
                                      'FBpp:temp_0', None, None, cvterm_id['polypeptide']))
            feature_id[pp_name] = cursor.fetchone()[0]

            # add synonyms
            cursor.execute(syn_sql, (pp_name, cvterm_id['symbol'], pp_name))
            symbol_id = cursor.fetchone()[0]

            # add feature_synonym
            cursor.execute(fs_sql, (symbol_id, mrna_id, pub_id, True))

            # add relationship to tr
            cursor.execute(feat_rel_sql, (feature_id[tr_name], feature_id[pp_name], cvterm_id['producedby']))
