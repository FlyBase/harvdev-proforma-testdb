
CREATE OR REPLACE FUNCTION make_fb_seqs(varchar(3)[])
 RETURNS VOID
AS $bob$
DECLARE 
  item CHARACTER VARYING;
  seq_name varchar(7);
BEGIN
  FOREACH item IN ARRAY $1 LOOP
    seq_name = item || '_seq';
    RAISE NOTICE 'created seq %', seq_name;
    EXECUTE 'CREATE SEQUENCE IF NOT EXISTS ' || seq_name;
  END LOOP;
END;
$bob$
LANGUAGE plpgsql;

SELECT make_fb_seqs(ARRAY['al', 'ti', 'tp', 'te', 'mc', 'ms', 'ba', 'ab', 'gn', 'tr', 'pp', 'og',
                          'cl', 'gg', 'hh', 'ig', 'lc', 'rf', 'sf', 'sn', 'st', 'tc', 'to', 'ch']);

CREATE OR REPLACE FUNCTION public.feature_assignname_fn_i()
 RETURNS trigger
AS $function$
DECLARE
  maxid      int;
  maxid_cg   int;
  id         varchar(255);
  id_fb      varchar(255);
  f_row_g feature%ROWTYPE;
  f_type  cvterm.name%TYPE;
  f_type_gene CONSTANT varchar :='gene';
  letter_t varchar;
  cg_accession dbxref.accession%TYPE;
  d_id    db.db_id%TYPE;
  f_dbxref_id feature.dbxref_id%TYPE;
  fd_id feature_dbxref.feature_dbxref_id%TYPE;
  f_uniquename feature.uniquename%TYPE;
  f_dbname_FB CONSTANT varchar :='FlyBase';
  f_dbname_gadfly CONSTANT varchar :='FlyBase Annotation IDs';
  seq_name varchar(7);
BEGIN
  RAISE NOTICE 'SINGLE enter feature_assignname_fn_i: feature.uniquename:%, feature.type_id:%', NEW.uniquename, NEW.type_id;
-- here assign new FBal, FBti, FBtp, FBte, FBmc, FBms, FBba, FBab, FBgn, FBtr, FBpp
  IF ( NEW.uniquename like 'FB%:temp%') THEN
    letter_t := substring(NEW.uniquename from 3 for 2);
    seq_name = letter_t || '_seq';
    SELECT INTO f_type c.name from feature f, cvterm c, organism o where f.type_id=c.cvterm_id and f.uniquename=NEW.uniquename and f.organism_id =NEW.organism_id;
    IF f_type is NOT NULL THEN
        RAISE NOTICE 'in feature_assignname_fn_i type of this feature is:%', f_type;
    END IF;
    IF (letter_t ='gn' AND f_type!='gene') THEN
    
    ELSE  
      RAISE NOTICE 'in f_i, feature type is:%', f_type;
      SELECT INTO f_row_g * from feature where uniquename=NEW.uniquename and organism_id=NEW.organism_id;      
      IF (letter_t = 'sf' or letter_t = 'og') THEN
        maxid = nextval(seq_name);
        IF maxid = 1 THEN
          SELECT INTO maxid max(to_number(substring(accession from 5 for 10), '9999999999'))+1 
            FROM dbxref dx, db d
            WHERE dx.db_id=d.db_id AND
                  d.name=f_dbname_FB AND
                  accession like 'FB'|| letter_t ||'__________';
        END IF;
	      IF maxid IS NULL THEN
          maxid:=1;
        END IF;
        SELECT INTO maxid setval(seq_name, maxid);
        RAISE NOTICE 'maxid after is:%', maxid;
        id:=lpad(CAST(maxid as TEXT), 10, '0000000000');

      ELSE
        maxid = nextval(seq_name);
        RAISE NOTICE 'MAX from seq is %', maxid;
        IF maxid = 1 THEN
          SELECT INTO maxid max(to_number(substring(accession from 5 for 7), '9999999'))+1 
            FROM dbxref dx, db d  
            WHERE dx.db_id=d.db_id AND
                d.name=f_dbname_FB AND
                accession like 'FB'|| letter_t || '_______';
          IF maxid IS NULL THEN
            maxid:=1;
          END IF;
          SELECT INTO maxid setval(seq_name, maxid);
        END IF; 
        RAISE NOTICE 'maxid after is:%', maxid;
        id:=lpad(CAST(maxid as TEXT), 7, '0000000');
      END IF;
    
      f_uniquename:=CAST('FB'|| letter_t||id as TEXT);

      SELECT INTO d_id db_id from db where name= f_dbname_FB;
      IF d_id IS NULL THEN 
        INSERT INTO db(name) values (f_dbname_FB);
        SELECT INTO d_id db_id from db where name= f_dbname_FB;
      END IF;
      RAISE NOTICE 'db_id:%, uniquename:%, f_dbname_FB:%:', d_id, f_uniquename, f_dbname_FB; 
      SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
      IF f_dbxref_id IS NULL THEN 
        INSERT INTO dbxref (db_id, accession) values(d_id, f_uniquename);
        SELECT INTO f_dbxref_id dbxref_id from dbxref where db_id=d_id and accession=f_uniquename;
      END IF;
      RAISE NOTICE 'dbxref_id:%', f_dbxref_id;
      RAISE NOTICE 'old uniquename of this feature is:%', f_row_g.uniquename;
      RAISE NOTICE 'new uniquename of this feature is:%', f_uniquename;
      UPDATE feature set uniquename=f_uniquename, dbxref_id=f_dbxref_id where feature_id=f_row_g.feature_id;
      SELECT INTO fd_id feature_dbxref_id from feature_dbxref where feature_id=f_row_g.feature_id and dbxref_id=f_dbxref_id;
      IF fd_id IS NULL THEN
        insert into feature_dbxref(is_current, feature_id, dbxref_id) values ('true',f_row_g.feature_id,f_dbxref_id);
      END IF;
    END IF;
  ELSE
    letter_t := substring(NEW.uniquename from 3 for 2);
    --IF (letter_t = 'gn') THEN
      RAISE NOTICE 'NOT temp?? %', NEW.uniquename;
      IF ( NEW.uniquename like 'FB%') THEN
          SELECT INTO maxid setval(letter_t || '_seq', 0);
      END IF;
    --END IF;
  END IF;
  RAISE NOTICE 'leave f_i .......';
  return NEW;    
END;
$function$
LANGUAGE plpgsql;