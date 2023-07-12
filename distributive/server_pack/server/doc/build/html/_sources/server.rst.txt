Server module
=================================================

Messenger server module.
Processes dictionaries - messages, stores public keys of clients.

Usage

The module supports command-side argent:

1. -p - Port on which connections are received
2. -a - Address from which connections are accepted.
3. --no_gui Start only basic functions, without graphical shell.

* Only 1 command is supported in this mode: "exit" for  exit.

Examples of use:

``python server.py -p 8080``

* Start a server on port 8080.*

``python server.py -a localhost``

*Start a server accepting only localhost connections.*

``python server.py --no-gui``

*Run without a graphical shell*

server.py
~~~~~~~~~~~

Скрипт server.py
-----------------

.. automodule:: server
	:members:

server_core.py
~~~~~~~~~~~~~~~

.. autoclass:: server.server_core.ServerMessageProcessor
	:members:

database.py
~~~~~~~~~~~

.. autoclass:: server.server_database.ServerStorage
	:members:

s_main_window.py
~~~~~~~~~~~~~~~~~~

.. autoclass:: server.s_main_window.MainWindow
	:members:

add_user.py
~~~~~~~~~~~~

.. autoclass:: server.add_user.RegisterUser
	:members:

remove_user.py
~~~~~~~~~~~~~~

.. autoclass:: server.remove_user.RemUserDialog
	:members:

config_window.py
~~~~~~~~~~~~~~~~

.. autoclass:: server.config_window.ConfigWindow
	:members:

stat_window.py
~~~~~~~~~~~~~~~~

.. autoclass:: server.stat_window.StatWindow
	:members: