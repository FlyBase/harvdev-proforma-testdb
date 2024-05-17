# create pubs


def add_pub_data(cursor, feature_id, cv_id, cvterm_id, db_id, db_dbxref):
    pub_sql = """ INSERT INTO pub (title, type_id, uniquename, pyear, miniref) VALUES (%s, %s, %s, %s, %s) RETURNING pub_id """
    pubprop_sql = """ INSERT INTO pubprop (pub_id, rank, type_id, value) VALUES (%s, %s, %s, %s) """
    editor_sql = """ INSERT INTO pubauthor (pub_id, rank, surname, givennames, editor) VALUES (%s, %s, %s, %s, %s) """
    pub_dbxref_sql = """ INSERT INTO pub_dbxref (pub_id, dbxref_id) VALUES (%s, %s) """

    for i in range(2, 9):
        cursor.execute(pub_sql, ('Nature_{}'.format(i), cvterm_id['computer file'], 'FBrf000000{}'.format(i), '1967', 'miniref_{}'.format(i)))
        pub_id = cursor.fetchone()[0]
        feature_id['Nature_{}'.format(i)] = pub_id
        print("Pub'{}' id = {}".format('Nature_{}'.format(i), pub_id))
        cursor.execute(pub_dbxref_sql, (pub_id, db_dbxref['pubmed'][f'{i}']))

    cursor.execute(pub_sql, ('unattributed', cvterm_id['unattributed'], 'unattributed', '1973', 'miniref_10'))
    pub_id = cursor.fetchone()[0]
    feature_id['unattributed'] = pub_id
    cursor.execute(pubprop_sql, (pub_id, 0, cvterm_id['curated_by'], "Curator:bob McBob...."))
    # cursor.execute(pubprop_sql, (pub_id, pubprop_rank, pubprop_type_id, pubprop_value))

    for i in range(1, 9):
        cursor.execute(pub_sql, ('CO_paper_{}'.format(i), cvterm_id['computer file'], 'FBrf100000{}'.format(i), '1967', 'miniref_{}'.format(i)))
        pub_id = cursor.fetchone()[0]
        feature_id['CO_paper_{}'.format(i)] = pub_id
        print("Pub'{}' id = {}".format('CO_paper_{}'.format(i), pub_id))

    temp_rank = 0
    for fly_ref in ('FBrf0104946', 'FBrf0105495'):
        temp_rank += 1
        cursor.execute(pub_sql, ('predefined pubs {}'.format(fly_ref[:3]), cvterm_id['FlyBase analysis'], fly_ref, '2000', 'miniref_{}'.format(temp_rank)))
        pub_id = cursor.fetchone()[0]
        cursor.execute(pubprop_sql, (pub_id, temp_rank, cvterm_id['curated_by'], "Curator:bob McBob...."))

    # multi pubs?
    parent_pub_sql = """ INSERT INTO pub (type_id, title, uniquename, pyear, miniref) VALUES (%s, %s, %s, %s, %s) RETURNING pub_id """
    cursor.execute(parent_pub_sql, (cvterm_id['journal'], 'Parent_pub2', 'multipub_2', '1967', 'Unused'))
    cursor.execute(parent_pub_sql, (cvterm_id['journal'], 'Parent_pub3', 'multipub_3', '1967', 'Mol. Cell'))
    parent_space_pub_id = cursor.fetchone()[0]
    cursor.execute(parent_pub_sql, (cvterm_id['journal'], 'Parent_pub1', 'multipub_1', '1967', 'Nature1'))

    parent_pub_id = cursor.fetchone()[0]
    pub_relationship_sql = """ INSERT INTO pub_relationship (type_id, subject_id, object_id) VALUES (%s, %s, %s) """
    for i in range(11, 16):
        cursor.execute(pub_sql, ('Paper_{}'.format(i), cvterm_id['paper'], 'FBrf00000{}'.format(i), '1967', 'miniref_{}'.format(i)))
        pub_id = cursor.fetchone()[0]
        cursor.execute(pub_relationship_sql, (cvterm_id['published_in'], pub_id, parent_pub_id))

    cursor.execute(pub_sql, ('Paper_29', cvterm_id['paper'], 'FBrf0000029', '1980', 'miniref_{}'.format(17)))
    parent_pub_id = cursor.fetchone()[0]

    # create general multipubs for testing
    for i in range(4, 14):
        cursor.execute(pub_sql, ('Journal_{}'.format(i+1), cvterm_id['journal'], 'multipub:temp_{}'.format(i), '2018', 'miniref_{}'.format(i+1)))
        pub_id = cursor.fetchone()[0]
        feature_id['Journal_{}'.format(i+1)] = pub_id
        cursor.execute(editor_sql, (pub_id, 1, 'Surname', 'one', True))
        cursor.execute(editor_sql, (pub_id, 2, 'Surname', 'two', True))
        cursor.execute(editor_sql, (pub_id, 3, 'Surname_{}'.format(i+1), 'Whatever', True))
        cursor.execute(pub_dbxref_sql, (pub_id, db_dbxref['issn']['1111-1111']))
        cursor.execute(pub_dbxref_sql, (pub_id, db_dbxref['issn']['2222-2222']))

    cursor.execute("select cvterm_id from cvterm where name = 'perscommtext' and cv_id = {}".format(cv_id['pubprop type']))
    cvterm_id['perscommtext'] = cursor.fetchone()[0]
    dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id"""

    for i in range(30, 36):
        cursor.execute(pub_sql, ('Paper_{}'.format(i), cvterm_id['paper'], 'FBrf00000{}'.format(i), '1980', 'miniref_{}'.format(i)))
        pub_id = cursor.fetchone()[0]
        cursor.execute(pub_relationship_sql, (cvterm_id['also_in'], pub_id, parent_pub_id))
        for j in range(1, 5):
            cursor.execute(pubprop_sql, (pub_id, j, cvterm_id["perscommtext"], "blah blah {}".format(j)))
            if i < 32:
                k = ((32 - i) * 10) + j
                cursor.execute(dbxref_sql, (db_id['isbn'], "{}".format(k)*5))
                new_dbxref_id = cursor.fetchone()[0]
                cursor.execute(pub_dbxref_sql, (pub_id, new_dbxref_id))

    # parent with miniref with space inside
    cursor.execute(pub_sql, ('Paper_Space', cvterm_id['paper'], 'FBrf0000020', '1967', 'miniref_{}'.format(20)))
    pub_id = cursor.fetchone()[0]
    cursor.execute(pub_relationship_sql, (cvterm_id['published_in'], pub_id, parent_space_pub_id))

    # canto stuff needs a pubmed added to FBrf0000020 Paper_Space
    cursor.execute(pub_dbxref_sql, (pub_id, db_dbxref['pubmed']['1']))

    return pub_id
