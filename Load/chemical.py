def add_chemical_data(cursor, cvterm_id, organism_id, dbxref_id, pub_id, db_id):
    """Add chemical data"""
    print("Adding chemical data.")

    pub_sql = """ SELECT pub_id FROM pub WHERE title = '{}' """
    chemical_sql = """ INSERT INTO feature (name, uniquename, organism_id, type_id, dbxref_id, is_obsolete)
                      VALUES (%s, %s, %s, %s, %s, %s) RETURNING feature_id"""
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id, is_current)
                 VALUES (%s, %s, %s, %s) """
    feat_pub_sql = """ INSERT INTO feature_pub (feature_id, pub_id) VALUEs (%s, %s)"""
    dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id"""
    featprop_sql = """ INSERT INTO featureprop (feature_id, type_id, rank, value)
                       VALUES (%s, %s, %s, %s) """
    chebi_publication_title = 'ChEBI: Chemical Entities of Biological Interest, EBI.'
    cursor.execute(pub_sql.format(chebi_publication_title))
    chem_pub_id = cursor.fetchone()[0]

    obsolete = False
    for i in range(6):
        cursor.execute(chemical_sql, ('octan-{}-ol'.format(i+1), 'FBch:temp_{}'.format(i+1),
                       organism_id['Dmel'], cvterm_id['chemical entity'], dbxref_id['{}'.format(i+1)], obsolete))
        chem_id = cursor.fetchone()[0]
        ##########
        # synonyms
        ##########
        # CHEBI:X
        cursor.execute(syn_sql, ('CHEBI:{}'.format(i+1), cvterm_id['symbol'], 'CHEBI:{}'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, pub_id, True))

        # OCTANOL-X, [symbol,fullname], is_current TRUE
        cursor.execute(syn_sql, ('OCTANOL-{}'.format(i+1), cvterm_id['symbol'], 'OCTANOL-{}'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, pub_id, True))

        cursor.execute(syn_sql, ('OCTANOL-{}'.format(i+1), cvterm_id['fullname'], 'OCTANOL-{}'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, pub_id, True))

        # OCT-X [symbol,fullname], is_current FALSE
        cursor.execute(syn_sql, ('OCT-{}'.format(i+1), cvterm_id['symbol'], 'OCT-{}'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, pub_id, False))

        cursor.execute(syn_sql, ('OCT-{}'.format(i+1), cvterm_id['fullname'], 'OCT-{}'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, pub_id, False))

        # Feat pub
        cursor.execute(feat_pub_sql, (chem_id,  chem_pub_id))
        if i != 4:  # first one only linked to chebi paper
            cursor.execute(feat_pub_sql, (chem_id,  pub_id))
        ############
        # Add props.
        ############
        # CH3b is_variant, value comes frmm CH3c
        cursor.execute(featprop_sql, (chem_id, cvterm_id['is_variant'], 0, f"var_{i+1}_1"))
        cursor.execute(featprop_sql, (chem_id, cvterm_id['is_variant'], 1, f"var_{i+1}_2"))
        # inchikey from chebi
        cursor.execute(featprop_sql, (chem_id, cvterm_id['inchikey'], 0, f"inchi_{i+1}_1"))
        # inexact_match CH3f
        cursor.execute(featprop_sql, (chem_id, cvterm_id['inexact_match'], 0, f"inex_{i+1}_1"))
        cursor.execute(featprop_sql, (chem_id, cvterm_id['inexact_match'], 1, f"inex_{i+1}_2"))
        # comment CH5a
        cursor.execute(featprop_sql, (chem_id, cvterm_id['comment'], 0, f"com_{i+1}_1"))
        cursor.execute(featprop_sql, (chem_id, cvterm_id['comment'], 1, f"com_{i+1}_2"))

    # create obsolete values for testing
    chems = (['carbon dioxide', '16526'],
             ['hydrogen peroxide', '16240'])
    obsolete = True
    for chem in chems:
        cursor.execute(dbxref_sql, (db_id['CHEBI'], chem[1]))
        dbxref_id = cursor.fetchone()[0]
        cursor.execute(chemical_sql, (chem[0], 'FBch00{}'.format(chem[1]),
                       organism_id['Dmel'], cvterm_id['chemical entity'], dbxref_id, obsolete))
        chem_id = cursor.fetchone()[0]
        cursor.execute(syn_sql, ("CHEBI:{}".format(chem[1]), cvterm_id['symbol'], "CHEBI:{}".format(chem[1])))
        # No PUB as obsolete and these would not have a pub
