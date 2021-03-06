#!/usr/bin/python
"""
:synopsis: Create data used in testing.

:moduleauthor: Ian Longden <ilongden@morgan.harvard.edu>

"""
import psycopg2
import os
import yaml
from Load.humanhealth import add_humanhealth_data
from Load.pubs import add_pub_data
from Load.db import add_db_data
from Load.organism import add_organism_data
from Load.singlebalancer import add_sb_data
from Load.div import add_div_data
from Load.gene_alleles import add_genes_and_alleles
from Load.tp_ti import create_tpti, create_tip
from Load.chemical import add_chemical_data

conn = psycopg2.connect(database="fb_test")
cursor = conn.cursor()

feature_count = 0

# Set variables to replace numbers in arrays.
RANK = 0
TITLE = 0
TYPE_ID = 1
SURNAME = 1
UNIQUENAME = 2
GIVENNAMES = 2
VALUE = 2
PYEAR = 3

# Global variables used throughout the script.
# may need to be passd to the Load.xxx functions.
cv_id = {}
db_id = {}
cvterm_id = {}
cv_cvterm_id = {}  # cv_cvterm_id[cvname][cvtermname] = cvterm_id
dbxref_id = {}     # dbxref[accession] = dbxref_id
db_dbxref = {}     # db_dbxref[dbname][acession] = dbxref_id
feature_id = {}    # feature_id[name] = feature_id
organism_id = {}   # organism_id['Hsap'] = organism_id

# Global SQL queries.
cv_sql = """  INSERT INTO cv (name) VALUES (%s) RETURNING cv_id"""
db_sql = """  INSERT INTO db (name) VALUES (%s) RETURNING db_id"""
dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id"""
cvterm_sql = """ INSERT INTO cvterm (dbxref_id, cv_id, name) VALUES (%s, %s, %s) RETURNING cvterm_id"""
pub_sql = """ INSERT INTO pub (title, type_id, uniquename, pyear, miniref) VALUES (%s, %s, %s, %s, %s) RETURNING pub_id """
pubprop_sql = """ INSERT INTO pubprop (pub_id, rank, type_id, value) VALUES (%s, %s, %s, %s) """
author_sql = """ INSERT INTO pubauthor (pub_id, rank, surname, givennames) VALUES (%s, %s, %s, %s) """
editor_sql = """ INSERT INTO pubauthor (pub_id, rank, surname, givennames, editor) VALUES (%s, %s, %s, %s, %s) """


def yaml_parse_and_dispatch():
    """Parse all yml files.

    A dictionary to choose the correct function to load data based on
    the filename from the yaml file. When adding new yamls, be sure to
    update this dictionary and create an appropriate function.
    """
    dispatch_dictionary = {
        'db_dbxref.yaml': load_db_dbxref,
        'cv_cvterm.yaml': load_cv_cvterm,
        'pub_author_pubprop.yaml': load_pub_author_pubprop
    }

    location = './data'

    # Need to load in a specific order due to CV term reliance.
    files_to_load = [
        'db_dbxref.yaml',
        'cv_cvterm.yaml',
        'pub_author_pubprop.yaml'
    ]

    for filename in files_to_load:
        with open(os.path.join(location, filename)) as yaml_location:
            yaml_to_process = yaml.full_load(yaml_location)

            # Filename is used as the lookup for the function.
            # Yaml data is based as a parameter.
            dispatch_dictionary[filename](yaml_to_process)


def load_db_dbxref(parsed_yaml):
    """Load db and dbxrefs."""
    db_acc = parsed_yaml

    for db in (db_acc.keys()):
        cursor.execute(db_sql, (db,))
        db_id[db] = cursor.fetchone()[0]
        print("adding dbxrefs for db {} [{}]".format(db, db_id[db]))

        for acc in db_acc[db]:
            cursor.execute(dbxref_sql, (db_id[db], acc))
            dbxref_id[acc] = cursor.fetchone()[0]
            if db not in db_dbxref:
                db_dbxref[db] = {}
            db_dbxref[db][acc] = dbxref_id[acc]


def load_cv_cvterm(parsed_yaml):
    """Load a CV (controlled Vocabulary)."""
    cv_cvterm = parsed_yaml
    START = 0
    NEW_DB = 1
    FORMAT = 2
    specific_dbs = {'SO':                       (0, 'SO', '{:07d}'),
                    'molecular_function':       (1000, 'GO', '{:07d}'),
                    'cellular_component':       (2000, 'GO', '{:07d}'),
                    'biological_process':       (3000, 'GO', '{:07d}'),
                    'FlyBase anatomy CV':       (1, 'FBbt', '{:08d}'),
                    'FlyBase miscellaneous CV': (1, 'FBcv', '{:07d}'),
                    'FlyBase development CV':   (1, 'FBdv', '{:08d}')}

    for cv_name in (cv_cvterm.keys()):
        cursor.execute(db_sql, (cv_name,))
        db_id[cv_name] = cursor.fetchone()[0]

        cursor.execute(cv_sql, (cv_name,))
        cv_id[cv_name] = cursor.fetchone()[0]

        print("adding cv {} [{}] and db [{}]".format(cv_name, cv_id[cv_name], db_id[cv_name]))
        # for specific cvterm we want to unique numbers as dbxrefs.
        if cv_name in specific_dbs:
            count = specific_dbs[cv_name][START]
        for cvterm_name in cv_cvterm[cv_name]:
            if cv_name in specific_dbs:
                db_name = specific_dbs[cv_name][NEW_DB]
            else:
                db_name = cv_name
            if cv_name in specific_dbs:
                # special, have different dbxref accession to cvterm name
                count += 1
                cursor.execute(dbxref_sql, (db_id[db_name], specific_dbs[cv_name][FORMAT].format(count)))
            else:
                cursor.execute(dbxref_sql, (db_id[cv_name], cvterm_name))
            dbxref_id[cvterm_name] = cursor.fetchone()[0]
            if cv_name not in db_dbxref:
                db_dbxref[cv_name] = {}
                cv_cvterm_id[cv_name] = {}
            db_dbxref[cv_name][cvterm_name] = dbxref_id[cvterm_name]
            cursor.execute(cvterm_sql, (dbxref_id[cvterm_name], cv_id[cv_name], cvterm_name))
            cvterm_id[cvterm_name] = cursor.fetchone()[0]
            cv_cvterm_id[cv_name][cvterm_name] = cvterm_id[cvterm_name]
            print("\t{} cvterm [{}] and dbxref [{}]".format(cvterm_name, cvterm_id[cvterm_name], dbxref_id[cvterm_name]))
    add_cvterm_namespace(cv_cvterm_id)


def add_cvterm_namespace(cv_cvterm_id):
    """Add namespace cvterm props.

    namespace name:  [[cvname ,cvtermname, typecvname, typecvtermname]...]
    example :-
    {experimental_tool_description: [['FlyBase miscellaneous CV', 'photoactivatable fluorescent protein',
                                      'feature_cvtermprop type', 'webcv']]}
    """
    cvtermprop_sql = """  INSERT INTO cvtermprop (cvterm_id, type_id, value, rank) VALUES (%s, %s, %s, %s) """
    namespaces = {'experimental_tool_descriptor': [['FlyBase miscellaneous CV', 'photoactivatable fluorescent protein',
                                                    'feature_cvtermprop type', 'webcv'],
                                                   ['FlyBase miscellaneous CV', 'protein detection tool',
                                                    'feature_cvtermprop type', 'webcv'],
                                                   ['FlyBase miscellaneous CV', 'RNA detection tool',
                                                    'feature_cvtermprop type', 'webcv']],
                  'phenotypic_class': [['FlyBase miscellaneous CV', 'pheno1', 'feature_cvtermprop type', 'webcv'],
                                       ['FlyBase miscellaneous CV', 'pheno2', 'feature_cvtermprop type', 'webcv'],
                                       ['FlyBase miscellaneous CV', 'pheno3', 'feature_cvtermprop type', 'webcv'],
                                       ['FlyBase miscellaneous CV', 'pheno4', 'feature_cvtermprop type', 'webcv'],
                                       ['FlyBase miscellaneous CV', 'pheno5', 'feature_cvtermprop type', 'webcv']],
                  'environmental_qualifier': [['FlyBase miscellaneous CV', 'environ1', 'feature_cvtermprop type', 'webcv'],
                                              ['FlyBase miscellaneous CV', 'environ2', 'feature_cvtermprop type', 'webcv']]}

    for value in namespaces.keys():
        rank = 0
        for item in namespaces[value]:
            cvterm_id = cv_cvterm_id[item[0]][item[1]]
            type_id = cv_cvterm_id[item[2]][item[3]]
            # add cvtermprop
            print("Adding cvterm prop '{}': '{}' - '{}'".format(value, item[1], item[3]))
            cursor.execute(cvtermprop_sql, (cvterm_id, type_id, value, rank))
            rank += 1


def load_pub_author_pubprop(parsed_yaml):
    """Load pub author data."""
    #################################
    # add pubs, pubprops, and authors
    #################################

    pub_author_pubprop = parsed_yaml

    for entry in pub_author_pubprop:

        pub_title = entry['pub'][TITLE]
        pub_type_id = cvterm_id[entry['pub'][TYPE_ID]]
        pub_uniquename = entry['pub'][UNIQUENAME]
        pub_pyear = entry['pub'][PYEAR]

        print("adding pub {}".format(pub_title))

        cursor.execute(pub_sql, (pub_title, pub_type_id, pub_uniquename, pub_pyear, 'miniref bob'))
        pub_id = cursor.fetchone()[0]

        for pubprop in entry['pubprop']:

            pubprop_rank = pubprop[RANK]
            pubprop_type_id = cvterm_id[pubprop[TYPE_ID]]
            pubprop_value = pubprop[VALUE]

            print("adding pubprop {}".format(pubprop_value))

            cursor.execute(pubprop_sql, (pub_id, pubprop_rank, pubprop_type_id, pubprop_value))

        for author in entry['author']:

            author_rank = author[RANK]
            author_surname = author[SURNAME]
            author_givennames = author[GIVENNAMES]

            print("adding author {} {}".format(author_surname, author_givennames))

            cursor.execute(author_sql, (pub_id, author_rank, author_surname, author_givennames))


############################
# Load data from YAML files.
############################


yaml_parse_and_dispatch()


#################
# Add organisms
#################
add_organism_data(cursor, organism_id, cvterm_id, db_id)


# add an enviroment ?
sql = """ INSERT INTO environment (uniquename) VALUES (%s) """
cursor.execute(sql, ('unspecified',))

for i in range(10):
    accession = "{:05d}".format(i+1)
    desc = "doid desc {}".format(i+1)
    cursor.execute(dbxref_sql, (db_id['DOID'], accession))
    dbxref = cursor.fetchone()[0]
    cursor.execute(cvterm_sql, (dbxref, cv_id['disease_ontology'], desc))

# provenance
cursor.execute(dbxref_sql, (db_id['FlyBase_internal'], 'FlyBase miscellaneous CV:provenance'))
dbxref_id['FlyBase miscellaneous CV:provenance'] = cursor.fetchone()[0]
cursor.execute(cvterm_sql, (dbxref_id['FlyBase miscellaneous CV:provenance'], cv_id['FlyBase miscellaneous CV'], "provenance"))
cvterm_id['provenance'] = cursor.fetchone()[0]
# projects need different db names and cv's
cvprop_sql = """ INSERT INTO cvtermprop (cvterm_id, type_id, value) VALUES (%s, %s, %s) """

# cursor.execute(db_sql, ('FBcv',))
# db_id['FBcv'] = cursor.fetchone()[0]

# project
cursor.execute(dbxref_sql, (db_id['FBcv'], '0003023'))
dbxref_id['0003023'] = cursor.fetchone()[0]
cursor.execute(cvterm_sql, (dbxref_id['0003023'], cv_id['FlyBase miscellaneous CV'], 'project'))
cvterm_id['project'] = cursor.fetchone()[0]
cursor.execute(cvprop_sql, (cvterm_id['project'], cvterm_id['webcv'], 'dataset_entity_type'))

# umbrella project
cursor.execute(dbxref_sql, (db_id['FBcv'], '0003030'))
dbxref_id['0003030'] = cursor.fetchone()[0]
cursor.execute(cvterm_sql, (dbxref_id['0003030'], cv_id['FlyBase miscellaneous CV'], 'umbrella project'))
cvterm_id['umbrella project'] = cursor.fetchone()[0]
cursor.execute(cvprop_sql, (cvterm_id['umbrella project'], cvterm_id['webcv'], 'project_type'))

#################
# feature has a dbxref_id but also we ALSO have another table feature_dbxref?
# feature_dbxref holds current and past values as it has is_current in it.
#################

conn.commit()
count = cursor.rowcount

###################
# create chromosome
###################

feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
                 VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""

cursor.execute(feat_sql, (None, organism_id['Dmel'], '2L', '2L', 'ACTGATG'*100, 700, cvterm_id['chromosome_arm']))
feature_id['2L'] = cursor.fetchone()[0]

cursor.execute(feat_sql, (None, organism_id['Dmel'], '2L', '2L', 'ACTGATG'*100, 700, cvterm_id['chromosome']))
cursor.execute(feat_sql, (None, organism_id['Dmel'], '2L', '2L', 'ACTGATG'*100, 700, cvterm_id['golden_path']))

cursor.execute(feat_sql, (None, organism_id['Dmel'], 'unspecified', 'unspecified', 'ACTGATG'*100, 700, cvterm_id['chromosome']))

# add bands
for beg in [94, 95]:
    for mid in 'ABCD':
        band = "band-{}{}".format(beg, mid)
        print("Adding band {}".format(band))
        cursor.execute(feat_sql, (None, organism_id['Dmel'], band, band, None, 0, cvterm_id['chromosome_band']))
        for end in range(1, 6):
            band = "band-{}{}{}".format(beg, mid, end)
            print("Adding band {}".format(band))
            cursor.execute(feat_sql, (None, organism_id['Dmel'], band, band, None, 0, cvterm_id['chromosome_band']))
            feature_id[band] = cursor.fetchone()[0]

# add pubs
pub_id = add_pub_data(cursor, feature_id, cv_id, cvterm_id, db_id, db_dbxref)

# add extra db's
add_db_data(cursor, db_id)


syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id) VALUES (%s, %s, %s) """
feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id) VALUES (%s, %s, %s) RETURNING feature_relationship_id """
feat_relprop_sql = """ INSERT INTO feature_relationshipprop (feature_relationship_id, type_id, value) VALUES (%s, %s, %s) """
feat_rel_pub = """ INSERT INTO feature_relationship_pub (feature_relationship_id, pub_id) VALUES (%s, %s) """

# create clones for some genes names to test duplicate names
for i in range(40, 50):
    # name = "FBcl{:07d}".format(i+1)
    print("Adding cDNA_clone {}".format(i+1))
    # create the clone feature
    cursor.execute(feat_sql, (None, organism_id['Dmel'], "symbol-{}".format(i+1),
                              'FBcl:temp_{}'.format(i), None, None, cvterm_id['cDNA_clone']))
    cdna_id = cursor.fetchone()[0]

# mRNA
for i in range(5):
    name = "FBtr{:07d}".format(i+1)
    print("Adding mRNA {}".format(i+1))
    # create the gene feature
    cursor.execute(feat_sql, (None, organism_id['Dmel'], "symbol-{}RA".format(i+1),
                              'FBtr:temp_0', None, None, cvterm_id['mRNA']))
    mrna_id = cursor.fetchone()[0]

    # add synonyms
    cursor.execute(syn_sql, ("fullname-{}".format(i+1), cvterm_id['fullname'], "fullname-{}RA".format(i+1)))
    name_id = cursor.fetchone()[0]
    cursor.execute(syn_sql, ("symbol-{}".format(i+1), cvterm_id['symbol'], "symbol-{}RA".format(i+1)))
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    cursor.execute(fs_sql, (name_id, mrna_id, pub_id))
    cursor.execute(fs_sql, (symbol_id, mrna_id, pub_id))

# Tools
for i in range(5):
    name = "FBto{:07d}".format(i+1)
    tool_sym = "Tool-sym-{}".format(i)
    print("Adding tool {}".format(tool_sym))
    # create the tool feature
    cursor.execute(feat_sql, (None, organism_id['Dmel'], tool_sym,
                              'FBto:temp_0', None, None, cvterm_id['engineered_region']))
    tool_id = cursor.fetchone()[0]

    # add synonyms
    cursor.execute(syn_sql, (tool_sym, cvterm_id['symbol'], tool_sym))
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    cursor.execute(fs_sql, (symbol_id, tool_id, pub_id))

create_tpti(cursor, feat_sql, syn_sql, fs_sql, organism_id, db_id, cvterm_id, pub_id, feature_id)

# transposable_element_insertion_site
for i in range(10):
    # name = "FBti{:07d}".format(i+1)
    tool_sym = "P{}TE{}{}".format('{', i+1, '}')
    print("Adding transposable_element_insertion_site {}".format(tool_sym))
    # create the ti feature
    create_tip(cursor, 'ti', tool_sym, organism_id['Dmel'], db_id, cvterm_id, feature_id, 'transposable_element_insertion_site', pub_id)


# transgenic_transposable_element
for i in range(10):
    # name = "FBtp{:07d}".format(i+1)
    print("Adding transgenic_transposable_element {}".format(i+1))
    tool_sym = "P{}TT{}{}".format('{', i+1, '}')
    # create the tool feature
    create_tip(cursor, 'tp', tool_sym, organism_id['Dmel'], db_id, cvterm_id, feature_id, 'transgenic_transposable_element', pub_id)

# engineered_plasmid
for i in range(10):
    # name = "FBmc{:07d}".format(i+1)
    tool_sym = "pP{}EC{}{}".format('{', i+1, '}')
    print("Adding engineered_plasmid {}".format(tool_sym))
    # create the tool feature
    cursor.execute(feat_sql, (None, organism_id['Dmel'], tool_sym,
                              'FBmc:temp_0', None, None, cvterm_id['engineered_plasmid']))
    tool_id = cursor.fetchone()[0]

    # add synonyms
    cursor.execute(syn_sql, (tool_sym, cvterm_id['symbol'], tool_sym))
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    cursor.execute(fs_sql, (symbol_id, tool_id, pub_id))

# aberation (chromosome_structure_variation)
for i in range(1, 11):
    # name = "FBmc{:07d}".format(i+1)
    tool_sym = "aberation-{}".format(i)
    print("Adding aberation {}".format(tool_sym))
    # create the tool feature
    cursor.execute(feat_sql, (None, organism_id['Dmel'], tool_sym,
                              'FBab:temp_0', None, None, cvterm_id['chromosome_structure_variation']))
    tool_id = cursor.fetchone()[0]
    feature_id[tool_sym] = tool_id

    # add synonyms
    cursor.execute(syn_sql, (tool_sym, cvterm_id['symbol'], tool_sym))
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    cursor.execute(fs_sql, (symbol_id, tool_id, pub_id))

    # feature_pub
    feat_pub_sql = """ INSERT INTO feature_pub (feature_id, pub_id) VALUEs (%s, %s)"""
    cursor.execute(feat_pub_sql, (tool_id, pub_id))

# create transposon
print("Adding transposon data.")
name = 'FBte0000001'
cursor.execute(feat_sql, (None, organism_id['Dmel'], 'P-element', 'FBte:temp_0', None, None, cvterm_id['natural_transposable_element']))
te_id = cursor.fetchone()[0]
# add synonyms
cursor.execute(syn_sql, ('P-element', cvterm_id['symbol'], 'P-element'))
symbol_id = cursor.fetchone()[0]
# add feature_synonym
cursor.execute(fs_sql, (symbol_id, te_id, pub_id))

# Cell line
print("Adding cell line data.")
cellline_sql = """ INSERT INTO cell_line (name, uniquename, organism_id) VALUES (%s, %s, %s) """
cursor.execute(cellline_sql, ('cellline1', 'cellline1', organism_id['Dmel']))

# Chemical data
add_chemical_data(cursor, cvterm_id, organism_id, dbxref_id, pub_id, db_id)
# print("Adding chemical data.")
# chemical_sql = """ INSERT INTO feature (name, uniquename, organism_id, type_id, dbxref_id) VALUES (%s, %s, %s, %s, %s) """
# cursor.execute(chemical_sql, ('octan-1-ol', 'FBch0016188', organism_id['Dmel'], cvterm_id['chemical entity'], dbxref_id['16188']))
# cursor.execute(syn_sql, ('CHEBI:16188', cvterm_id['symbol'], 'CHEBI:16188'))

# Gene grp
print("Adding gene grp data.")
grp_sql = """ INSERT INTO grp (name, uniquename, type_id) VALUES(%s, %s, %s) """
cursor.execute(grp_sql, ("TEST_GENE_GROUP", "FBgg:temp_0", cvterm_id['gene_group']))


# strain
print("Adding strain data.")
str_sql = """ INSERT INTO strain (uniquename, name, organism_id)
              VALUES (%s, %s, %s) RETURNING strain_id """
str_fs_sql = """ INSERT INTO strain_synonym (synonym_id, strain_id,  pub_id)
                 VALUES (%s, %s, %s) """
for i in range(1, 11):
    name = "STRAIN-{}".format(i)
    cursor.execute(str_sql, ("FBsn:temp_{}".format(i), name, organism_id['Dmel']))
    str_id = cursor.fetchone()[0]

    cursor.execute(syn_sql, (name, cv_cvterm_id['synonym type']['symbol'], name))
    symbol_id = cursor.fetchone()[0]

    # add strain_synonym
    cursor.execute(str_fs_sql, (symbol_id, str_id, pub_id))

# library
print("Adding library data.")
str_sql = """ INSERT INTO library (uniquename, name, type_id, organism_id)
              VALUES (%s, %s, %s, %s) RETURNING library_id """
str_fs_sql = """ INSERT INTO library_synonym (synonym_id, library_id,  pub_id)
                 VALUES (%s, %s, %s) """
for i in range(1, 11):
    name = "LIBRARY-{}".format(i)
    cursor.execute(str_sql, ("FBlc:temp_{}".format(i), name, cv_cvterm_id['FlyBase miscellaneous CV']['reagent collection'], organism_id['Dmel']))
    str_id = cursor.fetchone()[0]

    cursor.execute(syn_sql, (name, cv_cvterm_id['synonym type']['symbol'], name))
    symbol_id = cursor.fetchone()[0]

    # add library_synonym
    cursor.execute(str_fs_sql, (symbol_id, str_id, pub_id))


# add chromosome_structure_variation
print("Adding chromosome_structure_variation data.")
add_sb_data(cursor, organism_id, cv_cvterm_id, feature_id, pub_id, db_dbxref)

# create feature relationship between 'single balancers' and ' aberations
fr_sql = """ INSERT INTO feature_relationship (subject_id, object_id, type_id) VALUES (%s, %s, %s) RETURNING feature_relationship_id """
frp_sql = """ INSERT INTO feature_relationship_pub (feature_relationship_id, pub_id) VALUES(%s, %s) """

for i in range(1, 11):
    sb_name = "SINGBAL{}".format(i)
    ab_name = "aberation-{}".format(i)
    cursor.execute(fr_sql, (feature_id[sb_name], feature_id[ab_name], cvterm_id['carried_on']))
    fr_id = cursor.fetchone()[0]
    cursor.execute(frp_sql, (fr_id, pub_id))

# add genes
add_genes_and_alleles(cursor, organism_id, feature_id, cvterm_id, dbxref_id, db_id, pub_id)

# Add Proteins
for i in range(5):
    name = "FBpp{:07d}".format(i+1)
    print("Adding protein {}".format(i+1))
    # create the protein feature
    cursor.execute(feat_sql, (None, organism_id['Dmel'], "pp-symbol-{}".format(i+1),
                              'FBpp:temp_0', None, None, cvterm_id['polypeptide']))
    protein_id = cursor.fetchone()[0]

    # add synonyms
    cursor.execute(syn_sql, ("pp-fullname-{}".format(i+1), cvterm_id['fullname'], "pp-fullname-{}".format(i+1)))
    name_id = cursor.fetchone()[0]
    cursor.execute(syn_sql, ("pp-symbol-{}".format(i+1), cvterm_id['symbol'], "pp-symbol-{}".format(i+1)))
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    cursor.execute(fs_sql, (name_id, protein_id, pub_id))
    cursor.execute(fs_sql, (symbol_id, protein_id, pub_id))

    # add feature_relationship to allele and prop for it
    cursor.execute(feat_rel_sql, (feature_id["al-symbol-{}".format(i+1)], protein_id, cvterm_id['representative_isoform']))
    fr_id = cursor.fetchone()[0]
    print("fr_id = {}, type = {}".format(fr_id, cvterm_id['fly_disease-implication_change']))
    cursor.execute(feat_relprop_sql, (fr_id, cvterm_id['fly_disease-implication_change'], 'frp-{}'.format(i+1)))
    cursor.execute(feat_rel_pub, (fr_id, pub_id))

# Humanhealth
add_humanhealth_data(cursor, feature_id, cv_id, cvterm_id, db_id, db_dbxref, pub_id, organism_id['Hsap'])

# Disease Implicated Variants (DIV)
add_div_data(cursor, organism_id, cv_cvterm_id, feature_id, pub_id, db_dbxref)

conn.commit()
conn.close()
print("SUCCESS")
