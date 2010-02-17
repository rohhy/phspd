00 - initialize enviromant
   - mkdir certs
   - mkdir private
   - echo 100002 > serial
   - touch certindex.txt
   - copy openssl.conf

01 - Generate a self-signed certificate (http://code.activestate.com/recipes/442473/)
  openssl req -new -x509 -keyout private/ca-key.pem -out ca-cert.pem -days 365 -nodes -config ./openssl.cnf

02 - Generate server request and sign
  openssl req -new -x509 -nodes -out server-req.pem -keyout private/server-key.pem -days 365 -config ./openssl.cnf
  openssl ca -out server-cert.pem -days 365 -config ./openssl.cnf -infiles server-req.pem

03 - Generate client request and sign
  openssl req -new -x509 -nodes -out client-req.pem -keyout private/client-key.pem -days 365 -config ./openssl.cnf
  openssl ca -out client-cert.pem -days 365 -config ./openssl.cnf -infiles client-req.pem

04 - generate PKCS#12 file
  openssl pkcs12 -export -in client-cert.pem -inkey private/client-key.pem -certfile ca-cert.pem -name "[friendly name]" -out client-cert.p12

05 - files
  client-cert.p12
  cat server-cert.pem private/server-key.pem ca-cert.pem > server.pem



---------------------------------
- ca request
  openssl req -new -keyout cakey.pem -out careq.pem
- sign ca
  openssl x509 -req -in careq.pem -extensions v3_ca -signkey cakey.pem
    -out cacert.pem -days 3650
- verify ca
  openssl x509 -subject -issuer -enddate -noout -in cacert.pem


- server req
  openssl req -new -keyout serverkey.pem -out serverreq.pem
- sign server
  openssl x509 -req -in serverreq.pem -extensions usr_cert -CA cacert.pem
    -CAkey cakey.pem -CAcreateserial -out servercert.pem -days 365
- cumulative server file
  cat servercert.pem serverkey.pem cacert.pem > server.pem


- cleint req
  openssl req -new -keyout clientkey.pem -out clientreq.pem
- sign client
  openssl x509 -req -in clientreq.pem -CA cacert.pem -CAkey cakey.pem
    -CAcreateserial -out clientcert.pem -days 365
- to pkcs12 cerificate
  openssl pkcs12 -export -in clientcert.pem -inkey clientkey.pem
    -certfile cacert.pem -name "firefox client cerificate" -out clientcert.p12
