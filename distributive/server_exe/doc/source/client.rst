Client module documentation
=================================================

A client-side messaging application. Supports
sending messages to users who are on the network, messages are encrypted
using the RSA algorithm with a key length of 2048 bits.

Supports command line arguments:

``python client.py -a {ip_address} -n or --name {username} -p or -password {user's password}``

1. {server name} - the address of the message server.
2. {port} - the port on which connections are accepted
3. -n or --name - the name of the user who will be logged in.
4. -p or --password - the user's password.

All command line options are optional, but username and password must be used in tandem.

Examples of use:

* ``python client.py``

*Starting the application with default parameters.*

``python client.py ip_address some_port``

*Start application with instructions to connect to the server at ip_address:port*

``python -n test1 -p 123``

*Starting the application with user test1 and password 123*

``python client.py ip_address some_port -n test1 -p 123``

*Run the application with user test1 and password 123 and instructed to connect to the server at ip_address:port*

client.py
~~~~~~~~~

The running module contains a command line argument parser and application initialization functionality.

client. **arg_parser** ()
    Command line argument parser, returns a tuple of 4 elements:

	* server address
	* port
	* username
	* password

    Checks if the port number is correct.

database.py
~~~~~~~~~~~~~~

.. autoclass:: client.client_database.ClientDatabase
	:members:
	
transport.py
~~~~~~~~~~~~~~

.. autoclass:: client.transport.ClientTransport
	:members:

main_window.py
~~~~~~~~~~~~~~

.. autoclass:: client.main_window.ClientMainWindow
	:members:

start_dialog.py
~~~~~~~~~~~~~~~

.. autoclass:: client.client_start_dialog.UserNameDialog
	:members:


add_contact.py
~~~~~~~~~~~~~~

.. autoclass:: client.add_contact.AddContactDialog
	:members:
	
	
del_contact.py
~~~~~~~~~~~~~~

.. autoclass:: client.del_contact.DelContactDialog
	:members:

decos.py
~~~~~~~~~~~~~~

.. automodule:: client.decos
     :members:


Script client_utils.py
-------------------------

.. automodule:: client.client_utils
     :members:


Script client_variables.py
----------------------------

Contains various global project variables.
