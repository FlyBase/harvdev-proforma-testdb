# Add chemical data
#
# which are chemical features
""" select * from feature where uniquename like 'FBch%';"""
# To view dbxrefs for these:-
""" select f.uniquename, f.name, db.name, dx.accession
        from feature f, dbxref dx, db db, feature_dbxref fdx
        where fdx.dbxref_id= dx.dbxref_id and
        fdx.feature_id = f.feature_id and
        dx.db_id = db.db_id and
        f.uniquename like 'FBch%';
"""
# To view synonyms
"""
select left(s.name, 20) as syn_name , left(s.synonym_sgml, 20) as sgml_name, cvt.name, fs.is_current, p.title
    from feature_synonym fs, synonym s, cvterm cvt, pub p
    where fs.synonym_id = s.synonym_id and
          fs.pub_id = p.pub_id and
          s.type_id = cvt.cvterm_id and
          fs.feature_id = 595;
"""


def add_chemical_data(cursor, cvterm_id, organism_id, dbxref_id, pub_id, db_id, feature_id):
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
                       VALUES (%s, %s, %s, %s) RETURNING featureprop_id"""
    fppub_sql = """ INSERT INTO featureprop_pub (featureprop_id, pub_id) VALUES (%s, %s) """
    f_dbx = """ INSERT INTO feature_dbxref (feature_id, dbxref_id)
                VALUES (%s, %s) """

    chebi_publication_title = 'ChEBI: Chemical Entities of Biological Interest, EBI.'
    cursor.execute(pub_sql.format(chebi_publication_title))
    chem_pub_id = cursor.fetchone()[0]

    pubchem_publication_title = 'PubChem, NIH.'
    cursor.execute(pub_sql.format(pubchem_publication_title))
    pubchem_pub_id = cursor.fetchone()[0]

    obsolete = False
    for i in range(30):
        cursor.execute(dbxref_sql, (db_id['CHEBI'], f"{i+1}"))
        chem_dbxref_id = cursor.fetchone()[0]
        ##################################################################################
        #  NOTE: Due to the uniquename of FBch:temp_* the dbxref is created automatically.
        # and the one supplied is ignored, or at least over written.
        ##################################################################################
        cursor.execute(chemical_sql, ('octan-{}-ol'.format(i+1), 'FBch:temp_{}'.format(i+1),
                       organism_id['Dmel'], cvterm_id['chemical entity'], chem_dbxref_id, obsolete))

        chem_id = cursor.fetchone()[0]

        ##########
        # synonyms
        ##########
        # CHEBI:X
        cursor.execute(syn_sql, ('CHEBI:{}'.format(i+1), cvterm_id['symbol'], 'CHEBI:{}'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, chem_pub_id, False))

        # Mimic what comes in from a proforma CH1a and CH1b
        # ! CH1a. Chemical name to use in FlyBase : SoftWater
        # ! CH1b. Chemical name used in reference (other than original source) :H2O

        # octan-X-ol, [symbol,fullname], is_current TRUE
        cursor.execute(syn_sql, ('octan-{}-ol'.format(i+1), cvterm_id['symbol'], 'octan-{}-ol'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, chem_pub_id, True))

        cursor.execute(syn_sql, ('octan-{}-ol'.format(i+1), cvterm_id['fullname'], 'octan-{}-ol'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, pub_id, True))
        cursor.execute(fs_sql, (syn_id, chem_id, chem_pub_id, True))
        if i > 10:
            cursor.execute(fs_sql, (syn_id, chem_id, pubchem_pub_id, True))

        # OCT-X [symbol,fullname], is_current FALSE
        cursor.execute(syn_sql, ('OCT-CH1B-{}'.format(i+1), cvterm_id['symbol'], 'OCT-{}'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, chem_pub_id, False))

        cursor.execute(syn_sql, ('OCT-CH1B-{}'.format(i+1), cvterm_id['fullname'], 'OCT-{}'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, chem_pub_id, False))

        # pretend comes from CHEBI
        cursor.execute(syn_sql, ('OCT-CHEBI-{}'.format(i+1), cvterm_id['symbol'], 'OCT-CHEBI-{}'.format(i+1)))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, chem_pub_id, False))

        # Feat pub
        cursor.execute(feat_pub_sql, (chem_id,  chem_pub_id))
        print(chem_pub_id)
        if i != 4:  # first one only linked to chebi paper ????????
            cursor.execute(feat_pub_sql, (chem_id,  feature_id['Journal_10']))

        ############
        # Add props.
        ############
        # CH3b is_variant, value comes frmm CH3c
        # leave one with no isvariant for testing
        if i not in [4, 13]:
            cursor.execute(featprop_sql, (chem_id, cvterm_id['is_variant'], 0, f"var_{i+1}_1"))
            fp_id = cursor.fetchone()[0]
            cursor.execute(fppub_sql, (fp_id, pub_id))

        # inchikey from chebi
        cursor.execute(featprop_sql, (chem_id, cvterm_id['inchikey'], 0, f"inchi_{i+1}_1"))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fppub_sql, (fp_id, pub_id))

        # inexact_match CH3f
        cursor.execute(featprop_sql, (chem_id, cvterm_id['inexact_match'], 0, f"inex_{i+1}_1"))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fppub_sql, (fp_id, pub_id))

        cursor.execute(featprop_sql, (chem_id, cvterm_id['inexact_match'], 1, f"inex_{i+1}_2"))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fppub_sql, (fp_id, pub_id))

        # comment CH5a
        cursor.execute(featprop_sql, (chem_id, cvterm_id['comment'], 0, f"com_{i+1}_1"))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fppub_sql, (fp_id, pub_id))

        cursor.execute(featprop_sql, (chem_id, cvterm_id['comment'], 1, f"com_{i+1}_2"))
        fp_id = cursor.fetchone()[0]
        cursor.execute(fppub_sql, (fp_id, pub_id))

        # Add feature_dbxref.
        cursor.execute(f_dbx, (chem_id, chem_dbxref_id))

        if i > 10:  # add pubchem for this chemical too.
            # Feat pub
            cursor.execute(feat_pub_sql, (chem_id,  pubchem_pub_id))
            # add dbxref
            cursor.execute(dbxref_sql, (db_id['PubChem'], f"{i+1}"))
            pubchem_dbxref_id = cursor.fetchone()[0]
            # Add feature_dbxref.
            cursor.execute(f_dbx, (chem_id, pubchem_dbxref_id))

            ##########
            # synonyms
            ##########
            # PubChem:X
            cursor.execute(syn_sql, ('PubChem:{}'.format(i+1), cvterm_id['symbol'], 'PubChem:{}'.format(i+1)))
            syn_id = cursor.fetchone()[0]
            cursor.execute(fs_sql, (syn_id, chem_id, pubchem_pub_id, False))
            # pubchem-X , just another one to make sure we get them all on deletion.
            cursor.execute(syn_sql, ('pubchem-{}'.format(i+1), cvterm_id['symbol'], 'pubchem-{}'.format(i+1)))
            syn_id = cursor.fetchone()[0]
            cursor.execute(fs_sql, (syn_id, chem_id, pubchem_pub_id, False))

    # create obsolete values for testing
    chems = (['carbon dioxide', '16526'],
             ['hydrogen peroxide', '16240'])
    obsolete = True
    for chem in chems:
        cursor.execute(dbxref_sql, (db_id['FlyBase'], f"FBch00{chem[1]}"))
        dbxref_id = cursor.fetchone()[0]
        cursor.execute(chemical_sql, (chem[0], 'FBch00{}'.format(chem[1]),
                       organism_id['Dmel'], cvterm_id['chemical entity'], dbxref_id, obsolete))
        chem_id = cursor.fetchone()[0]
        cursor.execute(syn_sql, ("CHEBI:{}".format(chem[1]), cvterm_id['symbol'], "CHEBI:{}".format(chem[1])))
        # No PUB as obsolete and these would not have a pub

        cursor.execute(dbxref_sql, (db_id['CHEBI'], chem[1]))
        dbxref_id = cursor.fetchone()[0]
        # Add feature_dbxref.
        cursor.execute(f_dbx, (chem_id, dbxref_id))

    # create greek values for testing
    chems = (['α-testchem1', 'alpha-testchem1', '16271'],
             ['α-testchem2', 'alpha-testchem2', '16272'])
    obsolete = False
    for chem in chems:
        cursor.execute(dbxref_sql, (db_id['FlyBase'], f"FBch00{chem[1]}"))
        dbxref_id = cursor.fetchone()[0]

        cursor.execute(chemical_sql, (chem[1], 'FBch00{}'.format(chem[2]),
                       organism_id['Dmel'], cvterm_id['chemical entity'], dbxref_id, obsolete))
        chem_id = cursor.fetchone()[0]

        cursor.execute(syn_sql, ("CHEBI:{}".format(chem[1]), cvterm_id['symbol'], "CHEBI:{}".format(chem[2])))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, pub_id, True))

        cursor.execute(syn_sql, (chem[1], cvterm_id['fullname'], chem[0]))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, feature_id['FBrf0243181'], True))

        # Add dbxref and feature_dbxref.
        cursor.execute(dbxref_sql, (db_id['CHEBI'], chem[2]))
        dbxref_id = cursor.fetchone()[0]
        cursor.execute(f_dbx, (chem_id, dbxref_id))

    # create pubchem only chemicals for renaming tests
    chems = (['p-carbon dioxide', '116526'],
             ['p-hydrogen peroxide', '116240'])
    obsolete = False
    for chem in chems:
        cursor.execute(dbxref_sql, (db_id['FlyBase'], f"FBch00{chem[1]}"))
        dbxref_id = cursor.fetchone()[0]
        cursor.execute(chemical_sql, (chem[0], 'FBch0{}'.format(chem[1]),
                       organism_id['Dmel'], cvterm_id['chemical entity'], dbxref_id, obsolete))
        chem_id = cursor.fetchone()[0]

        cursor.execute(syn_sql, ("PUBCHEM:{}".format(chem[1]), cvterm_id['symbol'], "PUBCHEM:{}".format(chem[1])))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, pub_id, True))

        cursor.execute(syn_sql, ("PUBCHEM:{}".format(chem[1]), cvterm_id['fullname'], "PUBCHEM:{}".format(chem[1])))
        syn_id = cursor.fetchone()[0]
        cursor.execute(fs_sql, (syn_id, chem_id, pub_id, True))

        cursor.execute(dbxref_sql, (db_id['PubChem'], chem[1]))
        dbxref_id = cursor.fetchone()[0]
        # Add feature_dbxref.
        cursor.execute(f_dbx, (chem_id, dbxref_id))
        cursor.execute(feat_pub_sql, (chem_id, pubchem_pub_id))
