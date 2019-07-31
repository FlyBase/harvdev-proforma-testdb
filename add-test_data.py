#!/usr/bin/python
import psycopg2
import os
  

def reset(cursor):
    # in reverse order of creation to avoid broken FK constraints etc
    tables = ['audit_chado',
              'humanhealthprop', 'humanhealth_synonym', 'humanhealth_cvterm', 'humanhealth', 
              'humanhealth_featureprop', 'humanhealth_feature',
              'cell_lineprop_pub', 'cell_lineprop', 'cell_line_synonym', 'cell_line_dbxref', 'cell_line_pub','cell_line',
              'strain',
              'feature_expression', 'expression',
              'feature_grpmember','grpmember', 'grp_dbxref', 'grp_relationship', 'grp_pub', 'grpprop', 'grp',
              'library_synonym', 'library_dbxref', 'library_pub', 'library',
              'feature_relationship','feature_synonym', 'feature_dbxref', 'feature_pub', 'featureloc', 'feature',
              'synonym', 'pub', 'cvterm', 'cv', 'dbxref', 'db', 
              'environment', 'organism']
    for table in tables:
        ## print("Deleting data from table {}".format(table))
        cursor.execute('delete from {}'.format(table))

    '''cursor.execute('delete from audit_chado')
    cursor.execute('delete from cell_line_synonym')
    cursor.execute('delete from strain')
    cursor.execute('delete from library_synonym')
    cursor.execute('delete from library_pub')
    cursor.execute('delete from library_dbxref')
    cursor.execute('delete from library')
    cursor.execute('delete from feature_synonym')
    cursor.execute('delete from synonym')
    cursor.execute('delete from featureloc')
    cursor.execute('delete from feature')
    cursor.execute('delete from pub')
    cursor.execute('delete from cvterm')
    cursor.execute('delete from cv')
    cursor.execute('delete from dbxref')
    cursor.execute('delete from db')
    cursor.execute('delete from environment')
    cursor.execute('delete from organism') '''
    # and now get rid of the sequence stuff so the number stay the same for each run
    # Not vital or anything just saves having to look things up later. (once you get used to the ids)
    sequences = ['feature_feature_id_seq', 'synonym_synonym_id_seq', 'feature_synonym_feature_synonym_id_seq',
                 'pub_pub_id_seq', 'pubprop_pubprop_id_seq', 'pubauthor_pubauthor_id_seq',
                 'feature_pub_feature_pub_id_seq', 'featureloc_featureloc_id_seq', 'db_db_id_seq',
                 'dbxref_dbxref_id_seq', 'cv_cv_id_seq', 'cvterm_cvterm_id_seq', 'feature_uniquename_seq',
                 'feature_feature_id_seq', 'organism_organism_id_seq', 'strain_strain_id_seq',
                 'synonym_synonym_id_seq', 'humanhealth_humanhealth_id_seq', 'humanhealth_dbxref_humanhealth_dbxref_id_seq',
                 'humanhealth_feature_humanhealth_feature_id_seq', 'humanhealth_featureprop_humanhealth_featureprop_id_seq',
                 'humanhealth_synonym_humanhealth_synonym_id_seq']

    for seq in (sequences):
        cursor.execute('ALTER SEQUENCE {} RESTART WITH 1'.format(seq))

conn = psycopg2.connect(database="fb_test")
cursor = conn.cursor()
# no need to reset, db is created each time
#reset(cursor)

feature_count = 0

#################
# Add an organism
#################
sql = """ insert into organism (abbreviation, genus, species, common_name) values (%s,%s,%s,%s) RETURNING organism_id"""
cursor.execute(sql, ('Dmel', 'Drosophila', 'melanogaster', 'fruit_fly'))
organism_id = cursor.fetchone()[0]
# Add human for FBhh etc.
cursor.execute(sql, ('Hsap', 'Homo', 'sapiens', 'Human'))
human_id = cursor.fetchone()[0]

# see if we add the following organisms we help things later on?
sql = """ insert into organism (species, genus) values (%s,%s) RETURNING organism_id"""
cursor.execute(sql, ( 'xenogenetic', 'Unknown'))
cursor.execute(sql, ( 'autogenetic', 'Unknown'))

# add an enviroment ?
sql = """ INSERT INTO environment (uniquename) VALUES (%s) """
cursor.execute(sql, ('unspecified',))

#################
# add a CV (controlled Vocabulary)
#################
cv_id = {}
cv_sql = """  insert into cv (name) values (%s) RETURNING cv_id"""

db_id = {}
db_sql = """  insert into db (name) values (%s) RETURNING db_id"""

dbxref_sql = """ INSERT INTO dbxref (db_id, accession) VALUES (%s, %s) RETURNING dbxref_id"""

cvterm_id = {}
cvterm_sql = """ INSERT INTO cvterm (dbxref_id, cv_id, name) values (%s, %s, %s) RETURNING cvterm_id"""

dbxref_id = {}

cv_cvterm = {'FlyBase': ['FlyBase analysis'],
             'FlyBase miscellaneous CV': ['unspecified', 'comment', 'natural population', 'single balancer',
                                          'faint', 'qualifier', 'assay', 'chemical entity',
                                          'in vitro construct - regulatory fusion', 'in vitro construct - coding region fusion',
                                          'in vitro construct - amino acid replacement',
                                          'evidence_code'],
             'SO': ['chromosome_arm', 'chromosome', 'gene', 'mRNA', 'DNA', 'golden_path_region','non-protein-coding_gene', 
                    'regulatory_region', 'chromosome_structure_variation', 'chromosomal_inversion',
                    'natural population', 'DNA_segment', 'transgenic_transposon', 'transposable_element',
                    'natural_transposable_element', 'gene_group', 'protein'],
             'synonym type': ['fullname', 'symbol', 'unspecified'],
             'pub type': ['computer file', 'unattributed', 'unspecified', 'personal communication to FlyBase',
                          'perscommtext', 'journal', 'paper'],
             'pubprop type': ['curated_by', 'languages', 'perscommtext', 'cam_flag', 'harv_flag', 'associated_text', 
                              'abstract_languages', 'not_Drospub', 'URL', 'pubmed_abstract', 'onto_flag', 'dis_flag',
                              'diseasenotes', 'deposited_files', 'graphical_abstract', 'internalnotes'],
             'relationship type': ['associated_with', 'belongs_to', 'attributed_as_expression_of', 'tagged_with',
                                   'alleleof', 'has_reg_region', 'representative isoform'],
             'pub relationship type': ['also_in', 'related_to', 'published_in'],
             'property type': ['comment', 'reported_genomic_loc', 'origin_comment', 'description', 'molobject_type',
                               'in_vitro_progenitor', 'balancer_status', 'members_in_db', 'data_link', 'stage',
                               'internalnotes', 'phenotype_description', 'hh_internal_notes', 'genetics_description', 'category',
                               'sub_datatype', 'data_link_bdsc', 'hh_ortholog_comment', 'molecular_info', 'disease_associated',
                               'propagate_transgenic_uses', 'fly disease-implication change', 'other disease-implication change',
                               'primary disease-implication change', 'additional disease-implication change', 'HDM comment',
                               'allele report comment'],
             'FlyBase_internal': ['pubprop type:curated_by'],
             'feature_cvtermprop type': ['wt_class', 'aberr_class', 'tool_uses', 'transgene_uses property', 'webcv'],
             'feature_pubprop type': ['abstract_languages'],
             'transgene_description': ['transposon'],
             'transgene_uses': ['characterization'],
             'library_cvtermprop type': ['lc2btype'],
             'FlyBase anatomy CV': ['embryo','dopaminergic PAM neuron 1', 'dopaminergic PAM neuron 5'],
             'FlyBase development CV': ['late embryonic stage', 'embryonic stage', 'adult stage'],
             'cell_lineprop type': ['internalnotes', 'lab_of_origin', 'comment'],
             'cell_line_relationship': ['targeted_mutant_from'],
             'grp property type': ['gg_description'],
             'grpmember type': ['grpmember_feature'],
             'experimental assays': ['distribution deduced from reporter (Gal4 UAS)'],
             'expression slots': ['stage', 'anatomy', 'assay'],
             'feature_expression property type': ['curated_as', 'comment'],
             'testdb': ['hh-1'],
             'GB': [],
             'DOI': [],
             'pubmed': [],
             'isbn': [],
             'PMCID': [],
             'DOID': [],
             'HGNC': [1, 2, 3, 4, 5],
             'ClinVar': ['ClinVar1', 'ClinVar2', 'ClinVar3', 'ClinVar4', 'ClinVar5'],
             'UniProtKB/Swiss-Prot': ['SW1', 'SW2', 'SW3', 'SW4', 'SW5'],
             'disease_ontology': ['hh-1'],
             'humanhealth_cvtermprop type': ['doid_term'],
             'humanhealth_featureprop type': ['dmel_gene_implicated', 'human disease relevant'],
             'humanhealth_pubprop type': []}

''' # testdb used in HH tests and other things
cursor.execute(db_sql, ('testdb',))
db_id['testdb'] = cursor.fetchone()[0]
cursor.execute(dbxref_sql, (db_id['testdb'], '1'))
  '''
for cv_name in (cv_cvterm.keys()):
    cursor.execute(db_sql, (cv_name,))
    db_id[cv_name] = cursor.fetchone()[0]

    cursor.execute(cv_sql, (cv_name,))
    cv_id[cv_name] = cursor.fetchone()[0]
    
    print("adding cv {} [{}] and db [{}]".format(cv_name, cv_id[cv_name], db_id[cv_name]))
 
    for cvterm_name in cv_cvterm[cv_name]:
        cursor.execute(dbxref_sql, (db_id[cv_name], cvterm_name))
        dbxref_id[cvterm_name] = cursor.fetchone()[0]
        cursor.execute(cvterm_sql, (dbxref_id[cvterm_name], cv_id[cv_name], cvterm_name))
        cvterm_id[cvterm_name] = cursor.fetchone()[0]
        print("\t{} cvterm [{}] and dbxref [{}]".format(cvterm_name, cvterm_id[cvterm_name], dbxref_id[cvterm_name]))

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

author_sql = """ INSERT INTO pubauthor (pub_id, rank, surname, givennames) VALUES (%s, %s, %s, %s) """
# create pubs
pub_id = 0
pub_sql = """ INSERT INTO pub (type_id, title, uniquename, pyear) VALUES (%s, %s, %s, %s) RETURNING pub_id """
pubprop_sql = """ INSERT INTO pubprop (pub_id, type_id, value, rank) VALUES (%s, %s, %s, %s) """
cursor.execute( pub_sql, (cvterm_id['computer file'], 'Nature', 'FBrf0000001', '1967'))
pub_id = cursor.fetchone()[0]
cursor.execute( pubprop_sql, (pub_id, cvterm_id['curated_by'], "Curator:bob McBob....", pub_id))
cursor.execute( pubprop_sql, (pub_id, cvterm_id["personal communication to FlyBase"], "1", pub_id))
cursor.execute( author_sql,(pub_id, 1, "Bueller", "Ferris"))
cursor.execute( author_sql,(pub_id, 2, "Bueller", "Katie"))
cursor.execute( author_sql,(pub_id, 3, "Bueller", "Jeannie"))
cursor.execute( author_sql,(pub_id, 4, "Bueller", "Tom"))
cursor.execute( author_sql,(pub_id, 5, "Frye", "Cameron"))



for i in range(2, 9):
    cursor.execute( pub_sql, (cvterm_id['computer file'], 'Nature_{}'.format(i), 'FBrf000000{}'.format(i), '1967'))
cursor.execute( pub_sql, (cvterm_id['unattributed'], 'unattributed', 'unattributed', '1973'))
pub_id = cursor.fetchone()[0]
cursor.execute( pubprop_sql, (pub_id, cvterm_id['curated_by'], "Curator:bob McBob....", pub_id))

for fly_ref in ('FBrf0104946', 'FBrf0105495'):
    cursor.execute( pub_sql, (cvterm_id['FlyBase analysis'], 'predefined pubs {}'.format(fly_ref[:3]), fly_ref ,'2000'))
    pub_id = cursor.fetchone()[0]
    cursor.execute( pubprop_sql, (pub_id, cvterm_id['curated_by'], "Curator:bob McBob....", pub_id))

# multi pubs?
parent_pub_sql = """ INSERT INTO pub (type_id, title, uniquename, pyear, miniref) VALUES (%s, %s, %s, %s, %s) RETURNING pub_id """
cursor.execute( parent_pub_sql, (cvterm_id['journal'], 'Parent_pub2', 'multipub_2', '1967', 'Unused'))
cursor.execute( parent_pub_sql, (cvterm_id['journal'], 'Parent_pub3', 'multipub_3', '1967', 'Mol. Cell'))
parent_space_pub_id = cursor.fetchone()[0]
cursor.execute( parent_pub_sql, (cvterm_id['journal'], 'Parent_pub1', 'multipub_1', '1967', 'Nature1'))

parent_pub_id = cursor.fetchone()[0]
pub_relationship_sql = """ INSERT INTO pub_relationship (type_id, subject_id, object_id) VALUES (%s, %s, %s) """
for i in range(11, 16):
    cursor.execute( pub_sql, (cvterm_id['paper'], 'Paper_{}'.format(i), 'FBrf00000{}'.format(i), '1967'))
    pub_id = cursor.fetchone()[0]
    cursor.execute( pub_relationship_sql, (cvterm_id['published_in'], pub_id, parent_pub_id))

cursor.execute( pub_sql, (cvterm_id['paper'], 'Paper_29', 'FBrf0000029', '1980'))
parent_pub_id = cursor.fetchone()[0]

# Quick fix for now, ensure we have the correct perscommtext in the cvterm dict 
cursor.execute("select cvterm_id from cvterm where name = 'perscommtext' and cv_id = {}".format(cv_id['pubprop type']))
cvterm_id['perscommtext'] = cursor.fetchone()[0]

pub_dbxref_sql = """ INSERT INTO pub_dbxref (pub_id, dbxref_id) VALUES (%s, %s) """
for i in range(30, 36):
    cursor.execute( pub_sql, (cvterm_id['paper'], 'Paper_{}'.format(i), 'FBrf00000{}'.format(i), '1980'))
    pub_id = cursor.fetchone()[0]
    cursor.execute( pub_relationship_sql, (cvterm_id['also_in'], pub_id, parent_pub_id))
    for j in range(1,5):
        cursor.execute(pubprop_sql, (pub_id, cvterm_id["perscommtext"], "blah blah {}".format(j), j))
        if i < 32:
            k = (( 32 - i) *10) + j
            cursor.execute(dbxref_sql, (db_id['isbn'], "{}".format(k)*5))
            new_dbxref_id = cursor.fetchone()[0]
            cursor.execute(pub_dbxref_sql, (pub_id, new_dbxref_id))

# parent with miniref with space inside
cursor.execute( pub_sql, (cvterm_id['paper'], 'Paper_Space'.format(i), 'FBrf0000020', '1967'))
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
feature_id = {}
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
feat_rel_sql = """ INSERT INTO feature_relationship (subject_id, object_id,  type_id) VALUES (%s, %s, %s) """

for i in range(5):
    name = "FBgn{:07d}".format(i+1)
    print("Adding gene {}".format(i+1))

    #create the gene feature
    cursor.execute(feat_sql, (None, organism_id, "symbol-{}".format(i+1),
                              'FBgn:temp_{}'.format(i+1), "ACTG"*50, 200, cvterm_id['gene']))
    gene_id = cursor.fetchone()[0]

    # add synonyms
    cursor.execute(syn_sql, ("fullname-{}".format(i+1), cvterm_id['fullname'], "fullname-{}".format(i+1)) )
    name_id = cursor.fetchone()[0]
    cursor.execute(syn_sql, ("symbol-{}".format(i+1), cvterm_id['symbol'], "symbol-{}".format(i+1)) )
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    cursor.execute(fs_sql, (name_id, gene_id, pub_id))
    cursor.execute(fs_sql, (symbol_id, gene_id, pub_id)) 

    # now add the feature loc
    cursor.execute(loc_sql, (gene_id, feature_id['2L'], i*100, (i+1)*100, 1))

    #add allele for each gene and add feature_relationship
    cursor.execute(feat_sql, (None, organism_id, "al-symbol-{}".format(i+1),
                              'FBal:temp_0', None, 200, cvterm_id['gene']))
    allele_id = cursor.fetchone()[0]
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

# human health
hh_sql = """ INSERT INTO humanhealth (name, uniquename, organism_id) VALUES (%s, %s, %s) RETURNING humanhealth_id """
hh_fs_sql = """ INSERT INTO humanhealth_synonym (synonym_id, humanhealth_id,  pub_id, is_current) VALUES (%s, %s, %s, %s) """
for i in range(5):
    print("Adding human health {}".format(i+1))
    # create human health feature, No need to attach to gene for now.
    cursor.execute(hh_sql, ("hh-name-{}".format(i+1), 'FBhh:temp_0', human_id))
    hh_id = cursor.fetchone()[0]

    # add synonyms
    cursor.execute(syn_sql, ("hh-fullname-{}".format(i+1), cvterm_id['fullname'], "hh-fullname-{}".format(i+1)) )
    name_id = cursor.fetchone()[0]
    cursor.execute(syn_sql, ("hh-symbol-{}".format(i+1), cvterm_id['symbol'], "hh-symbol-{}".format(i+1)) )
    symbol_id = cursor.fetchone()[0]

    # add feature_synonym
    cursor.execute(hh_fs_sql, (name_id, hh_id, pub_id, True))
    cursor.execute(hh_fs_sql, (symbol_id, hh_id, pub_id, True)) 

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
chemical_sql = """ INSERT INTO feature (name, uniquename, organism_id, type_id) VALUES (%s, %s, %s, %s) """
cursor.execute(chemical_sql, ('octanol', 'FBch0037868', organism_id, cvterm_id['chemical entity']))

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