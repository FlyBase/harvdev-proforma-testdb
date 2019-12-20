#################
# Add organisms
#################


def add_organism_data(cursor, organism_id, cvterm_id, db_id):
    dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id"""
    sql = """ insert into organism (abbreviation, genus, species, common_name) values (%s,%s,%s,%s) RETURNING organism_id"""

    cursor.execute(sql, ('Dmel', 'Drosophila', 'melanogaster', 'fruit_fly'))
    organism_id['Dmel'] = cursor.fetchone()[0]
    # Add human for FBhh etc.
    cursor.execute(sql, ('Hsap', 'Homo', 'sapiens', 'Human'))
    organism_id['Hsap'] = cursor.fetchone()[0]
    # add mouse (another mamalian)
    cursor.execute(sql, ('Mmus', 'Mus', 'musculus', 'laboratory mouse'))
    organism_id['Mmus'] = cursor.fetchone()[0]
    # add aritificial
    cursor.execute(sql, ('Zzzz', 'artificial', 'artificial', 'artificial/synthetic'))
    organism_id['Zzzz'] = cursor.fetchone()[0]

    ######################################################
    # add specific test organisms with dbxrefs and cvterms
    ######################################################
    org_dbxref_sql = """ insert into organism_dbxref (organism_id, dbxref_id) values (%s, %s) """
    org_prop_sql = """ insert into organismprop (organism_id, type_id, value, rank) values (%s, %s, %s, %s) """
    for i in range(5):
        cursor.execute(sql, ('T00{}'.format(i+1), 'Test_genus_{}'.format(i+1), 'Test_species_{}'.format(i+1), 'Test organism {}'.format(i+1)))
        test_species_id = cursor.fetchone()[0]

        # taxonid        - dbxref (db = NCBITaxon) single only
        cursor.execute(dbxref_sql, (db_id['NCBITaxon'], '{}'.format(i+1)))
        sp_dbxref = cursor.fetchone()[0]
        cursor.execute(org_dbxref_sql, (test_species_id, sp_dbxref))

        # taxon groups   - orgprop cvterm (multiple)
        for j in range(6):
            cursor.execute(org_prop_sql, (test_species_id, cvterm_id['taxgroup'], "val_{}".format(j+1), j+1))

        # official_db    - orgprop cvterm (single)
        cursor.execute(org_prop_sql, (test_species_id, cvterm_id['official_db'], "SP_test_{}".format(i+1), i+1))

    # see if we add the following organisms we help things later on?
    sql = """ insert into organism (species, genus) values (%s,%s) RETURNING organism_id"""
    cursor.execute(sql, ('xenogenetic', 'Unknown'))
    cursor.execute(sql, ('autogenetic', 'Unknown'))
