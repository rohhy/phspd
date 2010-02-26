#!/bin/bash
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

if [ -z $1 ]; then echo "usage: $0 [user-name]"; exit 1; fi
UNAME=$1

openssl req -new -keyout private/"$UNAME"key.pem -out reqs/"$UNAME"req.pem
openssl x509 -req -in reqs/"$UNAME"req.pem -CA certs/cacert.pem -CAkey private/cakey.pem -CAcreateserial -out certs/"$UNAME"cert.pem -days 365
openssl pkcs12 -export -in certs/"$UNAME"cert.pem -inkey private/"$UNAME"key.pem -certfile certs/cacert.pem -name "$UNAME client cerificate" -out pkcs12/"$UNAME".p12
