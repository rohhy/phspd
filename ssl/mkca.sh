#!/bin/bash
#openssl req -new -x509 -keyout private/ca-key.pem -out ca-cert.pem -days 365 -nodes -config ./openssl.cnf

openssl req -new -keyout ssl/private/cakey.pem -out ssl/reqs/careq.pem
openssl x509 -req -in ssl/reqs/careq.pem -extensions v3_ca -signkey ssl/private/cakey.pem -out ssl/certs/cacert.pem -days 3650
openssl x509 -subject -issuer -enddate -noout -in ssl/certs/cacert.pem 
