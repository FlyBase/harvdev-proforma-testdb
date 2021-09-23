def add_cell_line_data(cursor, organism_id, cv_cvterm_id, pub_id, feature_id):
    """Add cell_line data."""
    cellline_sql = """ INSERT INTO cell_line (name, uniquename, organism_id) VALUES (%s, %s, %s) RETURNING cell_line_id """
    celllineprop_sql = """ INSERT INTO cell_lineprop (cell_line_id, type_id, value, rank) VALUES (%s, %s, %s, %s) RETURNING cell_lineprop_id """
    celllineprop_pub_sql = """ INSERT INTO cell_lineprop_pub (cell_lineprop_id, pub_id) VALUES (%s, %s) """
    cellline_syn_sql = """ INSERT INTO cell_line_synonym (synonym_id, cell_line_id,  pub_id) VALUES (%s, %s, %s) """
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    for i in range(1, 11):
        name = 'cellline{}'.format(i)
        cursor.execute(cellline_sql, (name, name, organism_id['Dmel']))
        cellline_id = cursor.fetchone()[0]

        # add synonyms
        cursor.execute(syn_sql, (name, cv_cvterm_id['synonym type']['symbol'], name))
        symbol_id = cursor.fetchone()[0]

        # add cell_line__synonym
        cursor.execute(cellline_syn_sql, (symbol_id, cellline_id, pub_id))
        cursor.execute(cellline_syn_sql, (symbol_id, cellline_id, feature_id['unattributed']))

        # add props
        for prop_cvterm in ('source_strain', 'source_genotype', 'source_cross', 'lab_of_origin',
                            'karyotype', 'comment', 'internalnotes'):
            cursor.execute(celllineprop_sql, (cellline_id, cv_cvterm_id['cell_lineprop type'][prop_cvterm], "{}-{}".format(prop_cvterm, i), 0))
            celllineprop_id = cursor.fetchone()[0]
            cursor.execute(celllineprop_pub_sql, (celllineprop_id, pub_id))
