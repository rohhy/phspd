#!/bin/bash
rm -rf certs private reqs pkcs12

mkdir certs
mkdir private
mkdir reqs
mkdir pkcs12

echo 100001 > serial
touch certindex.txt

mkca.sh
mkserver.sh