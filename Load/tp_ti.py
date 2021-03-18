"""
Create data required to test FBtp and FBti.
"""


def create_tpti(cursor, feat_sql, syn_sql, fs_sql, organism_id, cvterm_id, pub_id):
    """Create FBtp and FBti data.

    transposable_element_insertion_site  ti
    transgenic_transposable_element      tp
    """
    # P-element ALready added
    # cursor.execute(feat_sql, (None, organism_id['Dmel'], 'P-element', 'FBte:temp_1', None, None, cvterm_id['natural_transposable_element']))

    for item_prefix in ('TP', 'TI'):
        for i in range(5):
            ti_feature_type_name = 'transposable_element_insertion_site'
            tp_feature_type_name = 'transgenic_transposable_element'
            species = 'Dmel'
            if item_prefix == 'TI':
                ti_feature_type_name = 'insertion_site'
                tp_feature_type_name = 'engineered_region'
                species = 'Ssss'
            tp_name = '{}{}{}{}'.format(item_prefix, '{', i+1, '}')
            ti_name = '{}BGG{}'.format(tp_name, i+1)
            print("Adding {} {}".format(tp_name, ti_name))
            # ti first
            cursor.execute(feat_sql, (None, organism_id['Dmel'], ti_name, 'FBti:temp_{}'.format(i), None, None, cvterm_id[ti_feature_type_name]))
            ti_id = cursor.fetchone()[0]

            # add synonyms
            cursor.execute(syn_sql, (ti_name, cvterm_id['symbol'], ti_name))
            ti_symbol_id = cursor.fetchone()[0]

            # add feature_synonym
            cursor.execute(fs_sql, (ti_symbol_id, ti_id, pub_id))

            # tp second
            cursor.execute(feat_sql, (None, organism_id[species], tp_name, 'FBtp:temp_{}'.format(i), None, None, cvterm_id[tp_feature_type_name]))
            tp_id = cursor.fetchone()[0]

            # add synonyms
            cursor.execute(syn_sql, (tp_name, cvterm_id['symbol'], tp_name))
            tp_symbol_id = cursor.fetchone()[0]

            # add feature_synonym
            cursor.execute(fs_sql, (tp_symbol_id, tp_id, pub_id))
