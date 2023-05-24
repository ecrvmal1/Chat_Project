from socket import *

def menu_action()
    result = int(input("enter code of action:\n"
                       "1 - connect to server"
                       "2 - message "
                       "3 - quit"
                       "4 - join to chat"
                       "5 - leave chat"
                       )
    return result





def client(ipaddress,port):
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((ipaddress, port))

    action = menu_action()
    print('action : ', action)