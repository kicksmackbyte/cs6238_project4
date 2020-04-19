#!/bin/bash

openssl genrsa -out client1.key 2048
openssl req -new -key client1.key -out client1.csr
openssl x509 -req -in client1.csr -CA CA.crt -CAkey ../../CA/CA.key -CAcreateserial -out client1.crt -days 1825 -sha256

