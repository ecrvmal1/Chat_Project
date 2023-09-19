# CHAT Project

The project is created for development and implementation 
Chat , based on Socket technology 
The project includes: 
- Server part, 
- Client part


## Project Stack

- Python > 3.7
  - Socket
  - Threads
  - PyQt5  (Client GUI)
  - SQLAlchemy
  - Select


Client authentication on server with RSA key;
e2e chat encryption with PKCS1_OAEP protocol;

## Python Packages
Server python package  can be loaded:
```shell
https://pypi.org/project/msnger-server/
```

Client python package  can be loaded:
```shell
https://pypi.org/project/msnger-client/
```
## Commands
Command to run Server:
```shell
Python server.py [-a <server_listen_address>(default '127.0.0.1' )] [-p <server_listen_port>(default =7777 )]
```

Command to run Client:
```shell
Python client.py -n <username> -p <password> [addr <server_listen_address> default '127.0.0.1'] [port <server_listen_port> def=7777]
```

## Лицензия

MIT
