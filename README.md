[![Build Status](https://travis-ci.com/FlyBase/harvdev-proforma-testdb.svg?token=7Nvc5gEdzuNraK13EL3s&branch=master)](https://travis-ci.com/FlyBase/harvdev-proforma-testdb)
# harvdev-proforma-testdb
```
docker build . -t proformatestdb

docker run -p 127.0.0.1:5436:5432 proformatestdb:latest

psql -h 127.0.0.1 -p 5436 -U tester -d fb_test  (password is *tester*)
```
## Example sql.
```
SELECT f.name, f.uniquename, cvt.name 
  FROM feature f, cvterm cvt 
  WHERE f.type_id = cvt.cvterm_id;

    name     | uniquename  |             name             
-------------+-------------+------------------------------
 2L          | 2L          | chromosome_arm
 unspecified | unspecified | chromosome
 2L          | 2L          | chromosome
 symbol-5    | FBgn0000005 | gene
 symbol-4    | FBgn0000004 | gene
 symbol-3    | FBgn0000003 | gene
 symbol-2    | FBgn0000002 | gene
 symbol-1    | FBgn0000001 | gene
 symbol-5RA  | FBtr0000005 | mRNA
 symbol-4RA  | FBtr0000004 | mRNA
 symbol-3RA  | FBtr0000003 | mRNA
 symbol-2RA  | FBtr0000002 | mRNA
 symbol-1RA  | FBtr0000001 | mRNA
 2L          | 2L          | golden_path_region
 P-element   | FBte0000001 | natural_transposable_element
```

## Use FlyBase dockerhub image
```
docker run -p 127.0.0.1:5436:5432 flybase/proformatestdb:latest
```

## Viewing Postgres logs

- The container must be running in order to view the logs.
- Connect to the running container.
  - `docker exec -it proformatestdb /bin/bash`

- Navigate to the log directory.
  -  `cd /var/log/postgresql`

- Use `tail`, `head`, or `cat` to view the logs.
  -  The log filename will change depending on the date.
  -  `tail -f postgresql-2019-07-23_200159.log`  
