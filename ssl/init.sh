#!/bin/bash
#Copyright Jan Rohacek 2010
#This program is distributed under the terms of the GNU General Public License.

rm -rf certs private reqs pkcs12

mkdir certs
mkdir private
mkdir reqs
mkdir pkcs12

echo 100001 > serial
touch certindex.txt

mkca.sh
mkserver.sh
