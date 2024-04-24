r"""
:synopsis: Create tp and ti using common formats for better testing,

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>

select * from feature where name like '%teis%';
 feature_id | dbxref_id | organism_id |        name        | uniquename  |       residues       | seqlen | md5checksum | type_id | is_analysis |      timeaccessioned       |      timelastmodified      | is_ob
solete
------------+-----------+-------------+--------------------+-------------+----------------------+--------+-------------+---------+-------------+----------------------------+----------------------------+------
-------
        821 |      1367 |           1 | teis1              | FBgn0000158 | ACTGACTGACTGACTGACTG |     20 |             |       3 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        822 |      1368 |           1 | teis1[Clk1]        | FBal0000223 |                      |      0 |             |      17 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        823 |      1369 |           1 | teis2              | FBgn0000159 | ACTGACTGACTGACTGACTG |     20 |             |       3 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        824 |      1370 |           1 | teis2[Clk1]        | FBal0000224 |                      |      0 |             |      17 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        825 |      1371 |           1 | teis3              | FBgn0000160 | ACTGACTGACTGACTGACTG |     20 |             |       3 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        826 |      1372 |           1 | teis3[Clk1]        | FBal0000225 |                      |      0 |             |      17 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        827 |      1373 |           1 | teis4              | FBgn0000161 | ACTGACTGACTGACTGACTG |     20 |             |       3 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        828 |      1374 |           1 | teis4[Clk1]        | FBal0000226 |                      |      0 |             |      17 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        829 |      1375 |           1 | teis5              | FBgn0000162 | ACTGACTGACTGACTGACTG |     20 |             |       3 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        830 |      1376 |           1 | teis5[Clk1]        | FBal0000227 |                      |      0 |             |      17 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        832 |      1378 |           1 | Mi{1}teis1[Clk1]   | FBti0000031 |                      |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        834 |      1380 |           1 | Mi{2}teis2[Clk1]   | FBti0000032 |                      |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        836 |      1382 |           1 | Mi{3}teis3[Clk1]   | FBti0000033 |                      |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        838 |      1384 |           1 | Mi{4}teis4[Clk1]   | FBti0000034 |                      |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        840 |      1386 |           1 | Mi{5}teis5[Clk1]   | FBti0000035 |                      |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        842 |      1388 |           1 | Mi{6}teis6[Clk1]   | FBti0000036 |                      |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        844 |      1390 |           1 | Mi{7}teis7[Clk1]   | FBti0000037 |                      |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        846 |      1392 |           1 | Mi{8}teis8[Clk1]   | FBti0000038 |                      |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        848 |      1394 |           1 | Mi{9}teis9[Clk1]   | FBti0000039 |                      |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        850 |      1396 |           1 | Mi{10}teis10[Clk1] | FBti0000040 |                      |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
(20 rows)

select * from feature where name like '%Mi%';
 feature_id | dbxref_id | organism_id |        name        | uniquename  | residues | seqlen | md5checksum | type_id | is_analysis |      timeaccessioned       |      timelastmodified      | is_obsolete
------------+-----------+-------------+--------------------+-------------+----------+--------+-------------+---------+-------------+----------------------------+----------------------------+-------------
        831 |      1377 |           1 | Mi{1}              | FBtp0000026 |          |        |             |      14 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        832 |      1378 |           1 | Mi{1}teis1[Clk1]   | FBti0000031 |          |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        833 |      1379 |           1 | Mi{2}              | FBtp0000027 |          |        |             |      14 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        834 |      1380 |           1 | Mi{2}teis2[Clk1]   | FBti0000032 |          |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        835 |      1381 |           1 | Mi{3}              | FBtp0000028 |          |        |             |      14 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        836 |      1382 |           1 | Mi{3}teis3[Clk1]   | FBti0000033 |          |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        837 |      1383 |           1 | Mi{4}              | FBtp0000029 |          |        |             |      14 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        838 |      1384 |           1 | Mi{4}teis4[Clk1]   | FBti0000034 |          |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        839 |      1385 |           1 | Mi{5}              | FBtp0000030 |          |        |             |      14 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        840 |      1386 |           1 | Mi{5}teis5[Clk1]   | FBti0000035 |          |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        841 |      1387 |           1 | Mi{6}              | FBtp0000031 |          |        |             |      14 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        842 |      1388 |           1 | Mi{6}teis6[Clk1]   | FBti0000036 |          |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        843 |      1389 |           1 | Mi{7}              | FBtp0000032 |          |        |             |      14 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        844 |      1390 |           1 | Mi{7}teis7[Clk1]   | FBti0000037 |          |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        845 |      1391 |           1 | Mi{8}              | FBtp0000033 |          |        |             |      14 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        846 |      1392 |           1 | Mi{8}teis8[Clk1]   | FBti0000038 |          |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        847 |      1393 |           1 | Mi{9}              | FBtp0000034 |          |        |             |      14 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        848 |      1394 |           1 | Mi{9}teis9[Clk1]   | FBti0000039 |          |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        849 |      1395 |           1 | Mi{10}             | FBtp0000035 |          |        |             |      14 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
        850 |      1396 |           1 | Mi{10}teis10[Clk1] | FBti0000040 |          |        |             |      15 | f           | 2024-04-22 15:41:43.399512 | 2024-04-22 15:41:43.399512 | f
(20 rows)

"""
from .gene_alleles import create_gene_alleles
from .tp_ti import create_tip

feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""
fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id, is_current) VALUES (%s, %s, %s, %s) """
syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id)
                   VALUES (%s, %s, %s) RETURNING feature_relationship_id """
dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id """


def create_teis(cursor, organism_id, feature_id, cvterm_id, dbxref_id, db_id, pub_id):

    create_gene_alleles(
        cursor, organism_id, feature_id, cvterm_id, db_id, pub_id,
        num_genes=5,
        num_alleles=1,
        gene_prefix='teis',
        allele_prefix=None,
        tool_prefix='Clk'
    )

    ti_feature_type_name = 'transposable_element_insertion_site'
    tp_feature_type_name = 'transgenic_transposable_element'
    for i in range(10):
        tp_name = "Mi{" + str(i+1) + '}'
        feature_id[tp_name] = create_tip(cursor, 'tp', tp_name, organism_id['Ssss'], db_id, cvterm_id, feature_id, tp_feature_type_name, pub_id)

        name = f"{tp_name}teis{i+1}[Clk1]"
        uniquename = f'FBti::temp_{i}'
        cursor.execute(dbxref_sql, (db_id['FlyBase'], uniquename))
        dbxref_id = cursor.fetchone()[0]

        cursor.execute(feat_sql,
                       (dbxref_id, organism_id['Dmel'], name, uniquename, None, None, cvterm_id[ti_feature_type_name]))
        tp_id = cursor.fetchone()[0]
        feature_id[name] = tp_id

        # add synonyms
        cursor.execute(syn_sql, (name, cvterm_id['symbol'], f"{tp_name}teis{i+1}<up>Clk1</up>"))
        tp_symbol_id = cursor.fetchone()[0]

        # add feature_synonym
        cursor.execute(fs_sql, (tp_symbol_id, tp_id, pub_id, True))
        #feature_id[ti_name] = create_tip(cursor, 'ti', ti_name, organism_id['Dmel'], db_id, cvterm_id, feature_id, ti_feature_type_name, pub_id)
