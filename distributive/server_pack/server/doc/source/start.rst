Start module
=================================================


A module for launching multiple clients at the same time.

Usage:

After startup, a prompt to enter a command will be displayed.
Supported commands:

1. s - Start Server

* Starts the server with default settings.

2. c - Start Clients

* A prompt will be displayed asking for the number of test clients to run.
* Clients will be started with names like **test1 - testX** and passwords **123**
* Test users must be manually registered on the server with the password **123** beforehand.
* If clients are started for the first time, startup time may be quite long due to generation of new RSA keys.

3. x - Close all windows

* Closes all active windows that were launched from this module.

4. q - End module

* Terminates the module

