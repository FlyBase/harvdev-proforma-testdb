#!/usr/bin/python
import psycopg2
import os
import yaml
from Load.humanhealth import add_humanhealth_data

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
cv_id = {}
db_id = {}
cvterm_id = {}
dbxref_id = {} # dbxref[accession] = dbxref_id
db_dbxref ={}  # db_dbxref[dbname][acession] = dbxref_id
feature_id = {} # feature_id[name] = feature_id

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
    # A dictionary to choose the correct function to load data based on
    # the filename from the yaml file. When adding new yamls, be sure to
    # update this dictionary and create an appropriate function.

    dispatch_dictionary = {
        'cv_cvterm.yaml': load_cv_cvterm,
        'pub_author_pubprop.yaml': load_pub_author_pubprop
    }

    location = './data'

    # Need to load in a specific order due to CV term reliance.
    files_to_load = [
        'cv_cvterm.yaml',
        'pub_author_pubprop.yaml'
    ]

    for filename in files_to_load:
        with open(os.path.join(location, filename)) as yaml_location:
            yaml_to_process = yaml.full_load(yaml_location)

            # Filename is used as the lookup for the function.
            # Yaml data is based as a parameter.
            dispatch_dictionary[filename](yaml_to_process)


def load_cv_cvterm(parsed_yaml):

    #################
    # add a CV (controlled Vocabulary)
    #################

    cv_cvterm = parsed_yaml

    for cv_name in (cv_cvterm.keys()):
        cursor.execute(db_sql, (cv_name,))
        db_id[cv_name] = cursor.fetchone()[0]

        cursor.execute(cv_sql, (cv_name,))
        cv_id[cv_name] = cursor.fetchone()[0]

        print("adding cv {} [{}] and db [{}]".format(cv_name, cv_id[cv_name], db_id[cv_name]))

        for cvterm_name in cv_cvterm[cv_name]:
            cursor.execute(dbxref_sql, (db_id[cv_name], cvterm_name))
            dbxref_id[cvterm_name] = cursor.fetchone()[0]
            if cv_name not in db_dbxref:
                db_dbxref[cv_name] = {}
            db_dbxref[cv_name][cvterm_name] = dbxref_id[cvterm_name]
            cursor.execute(cvterm_sql, (dbxref_id[cvterm_name], cv_id[cv_name], cvterm_name))
            cvterm_id[cvterm_name] = cursor.fetchone()[0]
            print("\t{} cvterm [{}] and dbxref [{}]".format(cvterm_name, cvterm_id[cvterm_name], dbxref_id[cvterm_name]))


def load_pub_author_pubprop(parsed_yaml):

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


def create_gene(organism_name, organism_id, gene_count):

    if organism_name == 'Dmel':
        sym_name = "symbol-{}".format(gene_count+1)
        fb_code = 'gn'
    else:
        sym_name = '{}\\symbol-{}'.format(organism_name, gene_count+1)
        fb_code = 'gn'  # Not og else get_feat_ukeys_by_name will not find them.

    print("Adding gene {} for species {} - syn {}".format(gene_count+1, organism_name, sym_name))

    #create the gene feature
    cursor.execute(feat_sql, (None, organism_id, sym_name,
                              'FB{}:temp_{}'.format(fb_code, gene_count+1), "ACTG"*5, 20, cvterm_id['gene']))
    feature_id[sym_name] = gene_id = cursor.fetchone()[0]

    # add synonyms
    if organism_name == 'Dmel':
        cursor.execute(syn_sql, ("fullname-{}".format(gene_count+1), cvterm_id['fullname'], "fullname-{}".format(gene_count+1)) )
        name_id = cursor.fetchone()[0]
    cursor.execute(syn_sql, (sym_name, cvterm_id['symbol'], sym_name) )
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    if organism_name == 'Dmel':
        cursor.execute(fs_sql, (name_id, gene_id, pub_id))
    cursor.execute(fs_sql, (symbol_id, gene_id, pub_id)) 

    # now add the feature loc
    cursor.execute(loc_sql, (gene_id, feature_id['2L'], gene_count*100, (gene_count+1)*100, 1)) 
    return gene_id


############################
# Load data from YAML files.
############################


yaml_parse_and_dispatch()


#################
# Add organisms
#################
sql = """ insert into organism (abbreviation, genus, species, common_name) values (%s,%s,%s,%s) RETURNING organism_id"""
cursor.execute(sql, ('Dmel', 'Drosophila', 'melanogaster', 'fruit_fly'))
organism_id = cursor.fetchone()[0]
# Add human for FBhh etc.
cursor.execute(sql, ('Hsap', 'Homo', 'sapiens', 'Human'))
human_id = cursor.fetchone()[0]
# add mouse (another mamalian)
cursor.execute(sql, ('Mmus', 'Mus', 'musculus', 'laboratory mouse'))
mouse_id = cursor.fetchone()[0]
# add aritificial
cursor.execute(sql, ('Zzzz', 'artificial', 'artificial', 'artificial/synthetic'))
artificial_id = cursor.fetchone()[0]

# see if we add the following organisms we help things later on?
sql = """ insert into organism (species, genus) values (%s,%s) RETURNING organism_id"""
cursor.execute(sql, ( 'xenogenetic', 'Unknown'))
cursor.execute(sql, ( 'autogenetic', 'Unknown'))

# add an enviroment ?
sql = """ INSERT INTO environment (uniquename) VALUES (%s) """
cursor.execute(sql, ('unspecified',))

# DOID:14330 "Parkinson's disease"
cursor.execute(dbxref_sql, (db_id['DOID'], '14330')) 
dbxref_id['14330'] = cursor.fetchone()[0]
cursor.execute(cvterm_sql, (dbxref_id['14330'], cv_id['disease_ontology'], "Parkinson's disease"))

#provenance
cursor.execute(dbxref_sql, (db_id['FlyBase_internal'], 'FlyBase miscellaneous CV:provenance')) 
dbxref_id['FlyBase miscellaneous CV:provenance'] = cursor.fetchone()[0]
cursor.execute(cvterm_sql, (dbxref_id['FlyBase miscellaneous CV:provenance'], cv_id['FlyBase miscellaneous CV'], "provenance"))

#projects need different db names and cv's 
cvprop_sql = """ INSERT INTO cvtermprop (cvterm_id, type_id, value) VALUES (%s, %s, %s) """

cursor.execute(db_sql, ('FBcv',))
db_id['FBcv'] = cursor.fetchone()[0]

# project
cursor.execute(dbxref_sql, (db_id['FBcv'], '0003023'))
dbxref_id['0003023'] = cursor.fetchone()[0]
cursor.execute(cvterm_sql, (dbxref_id['0003023'], cv_id['FlyBase miscellaneous CV'], 'project'))
cvterm_id['project'] = cursor.fetchone()[0]
cursor.execute(cvprop_sql, (cvterm_id['project'], cvterm_id['webcv'], 'dataset_entity_type'))

# umbrella project
#SELECT cvt.cvterm_id FROM cvterm cvt, cv, cvtermprop cvp, cvterm cvt2
#	      WHERE  cvt.name = 'umbrella project' and cvt.cv_id = cv.cv_id
#	        and  cv.name = 'FlyBase miscellaneous CV' and cvt.is_obsolete = 0 and cvt.cvterm_id = cvp.cvterm_id  
#	        and cvp.type_id = cvt2.cvterm_id and cvt2.name = 'webcv' and cvp.value = 'project_type'
cursor.execute(dbxref_sql, (db_id['FBcv'], '0003030'))
dbxref_id['0003030'] = cursor.fetchone()[0]
cursor.execute(cvterm_sql, (dbxref_id['0003030'], cv_id['FlyBase miscellaneous CV'], 'umbrella project'))
cvterm_id['umbrella project'] = cursor.fetchone()[0]
cursor.execute(cvprop_sql, (cvterm_id['umbrella project'], cvterm_id['webcv'], 'project_type'))

# create pubs
pub_id = 0

for i in range(2, 9):
    cursor.execute( pub_sql, ('Nature_{}'.format(i), cvterm_id['computer file'], 'FBrf000000{}'.format(i), '1967', 'miniref_{}'.format(i)))
cursor.execute( pub_sql, ('unattributed', cvterm_id['unattributed'], 'unattributed', '1973', 'miniref_10'))
pub_id = cursor.fetchone()[0]
cursor.execute(pubprop_sql, (pub_id, 0, cvterm_id['curated_by'], "Curator:bob McBob...."))
# cursor.execute(pubprop_sql, (pub_id, pubprop_rank, pubprop_type_id, pubprop_value))

temp_rank = 0
for fly_ref in ('FBrf0104946', 'FBrf0105495'):
    temp_rank += 1
    cursor.execute( pub_sql, ('predefined pubs {}'.format(fly_ref[:3]), cvterm_id['FlyBase analysis'], fly_ref ,'2000', 'miniref_{}'.format(temp_rank)))
    pub_id = cursor.fetchone()[0]
    cursor.execute(pubprop_sql, (pub_id, temp_rank, cvterm_id['curated_by'], "Curator:bob McBob...."))

# multi pubs?
parent_pub_sql = """ INSERT INTO pub (type_id, title, uniquename, pyear, miniref) VALUES (%s, %s, %s, %s, %s) RETURNING pub_id """
cursor.execute( parent_pub_sql, (cvterm_id['journal'], 'Parent_pub2', 'multipub_2', '1967', 'Unused'))
cursor.execute( parent_pub_sql, (cvterm_id['journal'], 'Parent_pub3', 'multipub_3', '1967', 'Mol. Cell'))
parent_space_pub_id = cursor.fetchone()[0]
cursor.execute( parent_pub_sql, (cvterm_id['journal'], 'Parent_pub1', 'multipub_1', '1967', 'Nature1'))

parent_pub_id = cursor.fetchone()[0]
pub_relationship_sql = """ INSERT INTO pub_relationship (type_id, subject_id, object_id) VALUES (%s, %s, %s) """
for i in range(11, 16):
    cursor.execute( pub_sql, ('Paper_{}'.format(i), cvterm_id['paper'], 'FBrf00000{}'.format(i), '1967', 'miniref_{}'.format(i)))
    pub_id = cursor.fetchone()[0]
    cursor.execute( pub_relationship_sql, (cvterm_id['published_in'], pub_id, parent_pub_id))

cursor.execute( pub_sql, ('Paper_29', cvterm_id['paper'], 'FBrf0000029', '1980', 'miniref_{}'.format(17)))
parent_pub_id = cursor.fetchone()[0]

# create general multipubs for testing
for i in range(4, 14):
    cursor.execute(pub_sql, ('Journal_{}'.format(i+1), cvterm_id['journal'], 'multipub:temp_{}'.format(i), '2018', 'miniref_{}'.format(i+1)))
    pub_id = cursor.fetchone()[0]
    cursor.execute(editor_sql, (pub_id, 1, 'Surname', 'one', True))
    cursor.execute(editor_sql, (pub_id, 2, 'Surname', 'two', True))
    cursor.execute(editor_sql, (pub_id, 3, 'Surname_{}'.format(i+1), 'Whatever', True))

# Quick fix for now, ensure we have the correct perscommtext in the cvterm dict 
cursor.execute("select cvterm_id from cvterm where name = 'perscommtext' and cv_id = {}".format(cv_id['pubprop type']))
cvterm_id['perscommtext'] = cursor.fetchone()[0]

pub_dbxref_sql = """ INSERT INTO pub_dbxref (pub_id, dbxref_id) VALUES (%s, %s) """
for i in range(30, 36):
    cursor.execute( pub_sql, ('Paper_{}'.format(i), cvterm_id['paper'], 'FBrf00000{}'.format(i), '1980', 'miniref_{}'.format(i)))
    pub_id = cursor.fetchone()[0]
    cursor.execute( pub_relationship_sql, (cvterm_id['also_in'], pub_id, parent_pub_id))
    for j in range(1,5):
        cursor.execute(pubprop_sql, (pub_id, j, cvterm_id["perscommtext"], "blah blah {}".format(j)))
        if i < 32:
            k = (( 32 - i) *10) + j
            cursor.execute(dbxref_sql, (db_id['isbn'], "{}".format(k)*5))
            new_dbxref_id = cursor.fetchone()[0]
            cursor.execute(pub_dbxref_sql, (pub_id, new_dbxref_id))

# parent with miniref with space inside
cursor.execute( pub_sql, ('Paper_Space'.format(i), cvterm_id['paper'], 'FBrf0000020', '1967', 'miniref_{}'.format(20)))
pub_id = cursor.fetchone()[0]
cursor.execute( pub_relationship_sql, (cvterm_id['published_in'], pub_id, parent_space_pub_id))

#################
# feature has a dbxref_id but also we ALSO have another table feature_dbxref?
# feature_dbxref holds current and past values as it has is_current in it.
#################

conn.commit()
count = cursor.rowcount
#print(count, ' Records added')

###########
# features
###########
"""
                                            Table "public.feature"
      Column      |            Type             |                          Modifiers                           
------------------+-----------------------------+--------------------------------------------------------------
 feature_id       | integer                     | not null default nextval('feature_feature_id_seq'::regclass)
 dbxref_id        | integer                     | 
 organism_id      | integer                     | not null
 name             | character varying(255)      | 
 uniquename       | text                        | not null
 residues         | text                        | 
 seqlen           | integer                     | 
 md5checksum      | character(32)               | 
 type_id          | integer                     | not null
 is_analysis      | boolean                     | not null default false
 timeaccessioned  | timestamp without time zone | not null default ('now'::text)::timestamp(6) with time zone
 timelastmodified | timestamp without time zone | not null default ('now'::text)::timestamp(6) with time zone
 is_obsolete      | boolean                     | not null default false
"""
###################
# create chromosome
# Hope i do not need the actual sequence
###################

feat_sql = """ INSERT INTO feature (dbxref_id, organism_id, name, uniquename, residues, seqlen, type_id)
                 VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING feature_id"""

cursor.execute(feat_sql, (None, organism_id, '2L', '2L', 'ACTGATG'*100, 700, cvterm_id['chromosome_arm']))
feature_id['2L'] = cursor.fetchone()[0]

cursor.execute(feat_sql, (None, organism_id, '2L', '2L', 'ACTGATG'*100, 700, cvterm_id['chromosome']))
cursor.execute(feat_sql, (None, organism_id, '2L', '2L', 'ACTGATG'*100, 700, cvterm_id['golden_path_region']))

cursor.execute(feat_sql, (None, organism_id, 'unspecified', 'unspecified', 'ACTGATG'*100, 700, cvterm_id['chromosome']))

##################
# create 5 genes
# including their locations
# and alleles
##################
loc_sql = """ INSERT INTO featureloc (feature_id, srcfeature_id, fmin, fmax, strand) VALUES (%s, %s, %s, %s, %s) """
fd_sql = """ INSERT INTO feature_dbxref (feature_id, dbxref_id) VALUES (%s, %s) """
dbx_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id """
syn_sql = """ INSERT INTO synonym (name, type_id, synonym_sgml) VALUES (%s, %s, %s) RETURNING synonym_id """
fs_sql = """ INSERT INTO feature_synonym (synonym_id, feature_id,  pub_id) VALUES (%s, %s, %s) """
feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id) VALUES (%s, %s, %s) RETURNING feature_relationship_id """
feat_relprop_sql = """ INSERT INTO feature_relationshipprop (feature_relationship_id, type_id, value) VALUES (%s, %s, %s) """
feat_rel_pub = """ INSERT INTO feature_relationship_pub (feature_relationship_id, pub_id) VALUES (%s, %s) """
alleles = []
for i in range(10):
 
    feature_id['gene'] = gene_id = create_gene('Dmel', organism_id, i)

    # create mouse and human genes
    create_gene('Hsap', human_id, i)
    create_gene('Mmus', mouse_id, i)
    create_gene('Zzzz', artificial_id, i)

    #add allele for each gene and add feature_relationship
    cursor.execute(feat_sql, (None, organism_id, "al-symbol-{}".format(i+1),
                              'FBal:temp_{}'.format(i), None, 200, cvterm_id['gene']))
    feature_id["al-symbol-{}".format(i+1)] = allele_id = cursor.fetchone()[0]
    alleles.append(allele_id)
    cursor.execute(feat_rel_sql, (allele_id, gene_id, cvterm_id['alleleof']))

    # add ClinVar dbxrefs to allele for testing changing description and removal
    for j in range(5):
        cursor.execute(fd_sql, (allele_id, dbxref_id['ClinVar{}'.format(j+1)]))
        
# Add Proteins
for i in range(5):
    name = "FBpp{:07d}".format(i+1)
    print("Adding protein {}".format(i+1))
    #create the protein feature
    cursor.execute(feat_sql, (None, organism_id, "pp-symbol-{}".format(i+1),
                              'FBpp:temp_0', None, None, cvterm_id['protein']))
    protein_id = cursor.fetchone()[0]

    # add synonyms
    cursor.execute(syn_sql, ("pp-fullname-{}".format(i+1), cvterm_id['fullname'], "pp-fullname-{}".format(i+1)) )
    name_id = cursor.fetchone()[0]
    cursor.execute(syn_sql, ("pp-symbol-{}".format(i+1), cvterm_id['symbol'], "pp-symbol-{}".format(i+1)) )
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    cursor.execute(fs_sql, (name_id, protein_id, pub_id))
    cursor.execute(fs_sql, (symbol_id, protein_id, pub_id)) 

    # add feature_relationship to allele and prop for it
    cursor.execute(feat_rel_sql, (alleles[i], protein_id, cvterm_id['representative_isoform']))
    fr_id = cursor.fetchone()[0]
    print("fr_id = {}, type = {}".format(fr_id, cvterm_id['fly_disease-implication_change']))
    cursor.execute(feat_relprop_sql, (fr_id, cvterm_id['fly_disease-implication_change'], 'frp-{}'.format(i+1)))
    cursor.execute(feat_rel_pub, (fr_id, pub_id))

# Humanhealth
add_humanhealth_data(cursor, feature_id, cv_id, cvterm_id, db_id, db_dbxref, gene_id, pub_id, human_id)


# mRNA
for i in range(5):
    name = "FBtr{:07d}".format(i+1)
    print("Adding mRNA {}".format(i+1))
    #create the gene feature
    cursor.execute(feat_sql, (None, organism_id, "symbol-{}RA".format(i+1),
                              'FBtr:temp_0', None, None, cvterm_id['mRNA']))
    mrna_id = cursor.fetchone()[0]

    # add synonyms
    cursor.execute(syn_sql, ("fullname-{}".format(i+1), cvterm_id['fullname'], "fullname-{}RA".format(i+1)) )
    name_id = cursor.fetchone()[0]
    cursor.execute(syn_sql, ("symbol-{}".format(i+1), cvterm_id['symbol'], "symbol-{}RA".format(i+1)) )
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    cursor.execute(fs_sql, (name_id, mrna_id, pub_id))
    cursor.execute(fs_sql, (symbol_id, mrna_id, pub_id)) 

 
# Tools
for i in range(5):
    name = "FBto{:07d}".format(i+1)
    print("Adding tool {}".format(i+1))
    tool_sym = "Tool-sym-{}".format(i)
    #create the tool feature
    cursor.execute(feat_sql, (None, organism_id, tool_sym,
                              'FBto:temp_0', None, None, cvterm_id['DNA_segment']))
    tool_id = cursor.fetchone()[0]

    # add synonyms
    cursor.execute(syn_sql, (tool_sym, cvterm_id['symbol'], tool_sym))
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    cursor.execute(fs_sql, (symbol_id, tool_id, pub_id)) 

# create transposon
print("Adding transposon data.")
name = 'FBte0000001'
cursor.execute(feat_sql, (None, organism_id, 'P-element', 'FBte:temp_0', None, None, cvterm_id['natural_transposable_element']))

# Cell line
print("Adding cell line data.")
cellline_sql = """ INSERT INTO cell_line (name, uniquename, organism_id) VALUES (%s, %s, %s) """
cursor.execute(cellline_sql, ('cellline1', 'cellline1', organism_id))

# Chemical data
print("Adding chemical data.")
chemical_sql = """ INSERT INTO feature (name, uniquename, organism_id, type_id, dbxref_id) VALUES (%s, %s, %s, %s, %s) """
cursor.execute(chemical_sql, ('octan-1-ol', 'FBch0016188', organism_id, cvterm_id['chemical entity'], dbxref_id['16188']))
cursor.execute(syn_sql, ('CHEBI:16188', cvterm_id['symbol'], 'CHEBI:16188'))

# Gene grp
grp_sql = """ INSERT INTO grp (name, uniquename, type_id) VALUES(%s, %s, %s) """
cursor.execute(grp_sql, ("TEST_GENE_GROUP", "FBgg:temp_0", cvterm_id['gene_group']))


# strain
#strain_id = {}
#strain_sql  = """ INSERT INTO strain (name, uniquename, organism_id) VALUES (%s, %s, %s) RETURNING strain_id """
#cursor.execute(strain_sql, ("Strain 1", "FBsn0000001", organism_id))
#strain_id["Strain 1"] = cursor.fetchone()[0]

#cursor.execute(strain_sql, ("Strain 2", "FBsn0000002", organism_id))
#strain_id["Strain 2"] = cursor.fetchone()[0]

conn.commit()
conn.close()
print("SUCCESS")