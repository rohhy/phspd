#!/bin/bash
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

openssl req -new -keyout private/serverkey.pem -out reqs/serverreq.pem
openssl x509 -req -in reqs/serverreq.pem -extensions usr_cert -CA certs/cacert.pem -CAkey private/cakey.pem -CAcreateserial -out servercert.pem -days 365
cat certs/servercert.pem private/serverkey.pem certs/cacert.pem > phspd.pem
