def add_chemical_data(cursor, cvterm_id, organism_id, dbxref_id, pub_id):
    """Add chemical data"""
    print("Adding chemical data.")

    pub_sql = """ SELECT pub_id FROM pub WHERE title = '{}' """
    chemical_sql = """ INSERT INTO feature (name, uniquename, organism_id, type_id, dbxref_id) VALUES (%s, %s, %s, %s, %s) RETURNING feature_id"""
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    feat_pub_sql = """ INSERT INTO feature_pub (feature_id, pub_id) VALUEs (%s, %s)"""

    chebi_publication_title = 'ChEBI: Chemical Entities of Biological Interest, EBI.'
    cursor.execute(pub_sql.format(chebi_publication_title))
    chem_pub_id = cursor.fetchone()[0]

    # pubchem_publication_title = 'PubChem, NIH.'
    # cursor.execute(pub_sql, (pubchem_publication_title)
    # pubchem_pub_id = cursor.fetchone()[0]

    for i in range(5):
        cursor.execute(chemical_sql, ('octan-{}-ol'.format(i+1), 'FBch:temp_{}'.format(i+1),
                       organism_id['Dmel'], cvterm_id['chemical entity'], dbxref_id['{}'.format(i+1)]))
        chem_id = cursor.fetchone()[0]
        cursor.execute(syn_sql, ('CHEBI:{}'.format(i+1), cvterm_id['symbol'], 'CHEBI:{}'.format(i+1)))
        cursor.execute(feat_pub_sql, (chem_id,  chem_pub_id))
        if i:  # first one only linked to chebi paper
            cursor.execute(feat_pub_sql, (chem_id,  pub_id))

