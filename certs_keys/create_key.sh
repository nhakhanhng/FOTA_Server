openssl req -new -out server.csr -newkey rsa:2048 -nodes -keyout server.key -config openssl.cnf
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt  -extensions req_ext -extfile openssl.cnf
openssl x509 -in server.crt -text -noout