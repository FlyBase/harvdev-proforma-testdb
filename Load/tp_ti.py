"""
Create data required to test FBtp and FBti.
"""


def create_tpti(cursor, feat_sql, syn_sql, fs_sql, organism_id, cvterm_id, pub_id):
    """Create FBtp and FBti data.

    transposable_element_insertion_site  ti
    transgenic_transposable_element      tp
    """
    for i in range(5):
        tp_name = 'TP{}{}{}'.format('{', i+1, '}')
        ti_name = '{}BGG{}'.format(tp_name, i+1)
        print("Adding {} {}".format(tp_name, ti_name))
        # ti first
        cursor.execute(feat_sql, (None, organism_id['Dmel'], ti_name, 'FBti:temp_{}'.format(i), None, None, cvterm_id['transposable_element_insertion_site']))
        ti_id = cursor.fetchone()[0]

        # add synonyms
        cursor.execute(syn_sql, (ti_name, cvterm_id['symbol'], ti_name))
        ti_symbol_id = cursor.fetchone()[0]

        # add feature_synonym
        cursor.execute(fs_sql, (ti_symbol_id, ti_id, pub_id))

        # tp second
        cursor.execute(feat_sql, (None, organism_id['Dmel'], tp_name, 'FBtp:temp_{}'.format(i), None, None, cvterm_id['transgenic_transposable_element']))
        tp_id = cursor.fetchone()[0]

        # add synonyms
        cursor.execute(syn_sql, (tp_name, cvterm_id['symbol'], tp_name))
        tp_symbol_id = cursor.fetchone()[0]

        # add feature_synonym
        cursor.execute(fs_sql, (tp_symbol_id, tp_id, pub_id))
