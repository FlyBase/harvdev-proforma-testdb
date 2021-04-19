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

feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""
fd_sql = """ INSERT INTO feature_dbxref (feature_id, dbxref_id) VALUES (%s, %s) """

gene_sub_count = 0


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
