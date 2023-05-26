import subprocess

PROCESS = []

while True:
    ANSWER = input('Choose action:\n'
                   'q- quit \n'
                   's- run server\n'
                   'x - close all windows')
    if ANSWER == 'q':
        break
    elif ANSWER == 's':
        PROCESS.append(subprocess.Popen('python server.py',
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))

        for i in range(5):
            PROCESS.append(subprocess.Popen('python client.py',
                                            creationflags=subprocess.CREATE_NEW_CONSOLE))

    elif ANSWER == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()


