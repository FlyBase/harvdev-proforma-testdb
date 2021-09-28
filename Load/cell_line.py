def add_cell_line_data(cursor, organism_id, cv_cvterm_id, pub_id, feature_id):
    """Add cell_line data."""
    cellline_sql = """ INSERT INTO cell_line (name, uniquename, organism_id) VALUES (%s, %s, %s) RETURNING cell_line_id """
    celllineprop_sql = """ INSERT INTO cell_lineprop (cell_line_id, type_id, value, rank) VALUES (%s, %s, %s, %s) RETURNING cell_lineprop_id """
    celllineprop_pub_sql = """ INSERT INTO cell_lineprop_pub (cell_lineprop_id, pub_id) VALUES (%s, %s) """
    cellline_syn_sql = """ INSERT INTO cell_line_synonym (synonym_id, cell_line_id,  pub_id) VALUES (%s, %s, %s) """
    syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
    cell_line_library_sql = """ INSERT INTO cell_line_library (cell_line_id, library_id, pub_id) VALUES (%s, %s, %s) RETURNING cell_line_library_id"""
    cell_line_libraryprop_sql = """ INSERT INTO cell_line_libraryprop (cell_line_library_id, type_id, rank) VALUES (%s, %s, %s) """
    cell_line_cvterm_sql = """ INSERT INTO  cell_line_cvterm (cell_line_id, cvterm_id, pub_id) VALUES (%s, %s, %s) RETURNING cell_line_cvterm_id"""
    cell_line_cvtermprop_sql = """ INSERT INTO  cell_line_cvtermprop (cell_line_cvterm_id, type_id, rank,value) VALUES (%s, %s, %s, %s) """
    count = 9100001
    for i in range(1, 11):
        name = 'cellline{}'.format(i)
        uniquename = "FBtc{}".format(count)
        count += 1
        cursor.execute(cellline_sql, (name, uniquename, organism_id['Dmel']))
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

        # add library
        cursor.execute(cell_line_library_sql, (cellline_id, feature_id['LIBRARY-{}'.format(i)], pub_id))
        cellline_library_id = cursor.fetchone()[0]
        # add libraryprop
        cursor.execute(cell_line_libraryprop_sql, (cellline_library_id, cv_cvterm_id['FlyBase miscellaneous CV']['reagent collection'], 0))

        # add cvterm
        # cvterm:(Cvterm id=70: name:'embryo' cv:(Cv id=19: name:'FlyBase anatomy CV'))
        cursor.execute(cell_line_cvterm_sql, (cellline_id, cv_cvterm_id['FlyBase anatomy CV']['embryo'], pub_id))
        # cvterm:(Cvterm id=77: name:'late embryonic stage' cv:(Cv id=20: name:'FlyBase development CV'))
        cursor.execute(cell_line_cvterm_sql, (cellline_id, cv_cvterm_id['FlyBase development CV']['late embryonic stage'], pub_id))

        # add cvtermprop
        cursor.execute(cell_line_cvterm_sql, (cellline_id, cv_cvterm_id['FlyBase miscellaneous CV']['male'], pub_id))
        cellline_cvterm_id = cursor.fetchone()[0]
        cursor.execute(cell_line_cvtermprop_sql, (cellline_cvterm_id, cv_cvterm_id['cell_line_cvtermprop type']['basis'], 0, "someval-{}".format(i)))
