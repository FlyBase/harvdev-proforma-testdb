# harvdev-proforma-testdb
docker build . -t bob

docker run -p 127.0.0.1:5432:5432 bob:latest


psql -h 127.0.0.1 -U tester -d fb_test  (password is *tester*)