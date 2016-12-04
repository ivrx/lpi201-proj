#!/usr/bin/python

import socket
import threading
import os.path
import time

class Server:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))

    def listen(self):
        self.s.listen(5)
        print "listening %s:%d" % (self.host, self.port)

        while True:
            conn, addr = self.s.accept()
            hostname = socket.gethostbyaddr(addr[0])[0]
            t = threading.Thread(target = self.listenToConnections, args = (conn, addr))

            conns.setConnection("%s - %s" % (hostname, addr[0]), conn, t)



    def listenToConnections(self, conn, addr):
        buffersize = 1024
        print addr

        while True:
            try:
                data = conn.recv(buffersize)
                if data:
                    print "%s: %s" % (addr[0], data)
                else:
                    print "disconnect"
                    raise Exception
            except:
                conn.close()
                return False

class Connections:

    def __init__(self):
        self.connections = {}

    def setConnection(self, hostname, conn, t):
        self.connections[hostname] = {'socket': conn, 'thread': t}

    def getConnections(self):
        return self.connections


def show_clients ():
    print "in show clients"
    clients = conns.getConnections()

    print clients

    for client in clients:
        print client

    back_to_menu()

def send_commands ():
    clientsHelper('Execute command: ', 'EXEC', send_commands)

def transfer_file ():
    # will need to refactor :/

    clients = conns.getConnections()
    if clients.__len__() == 0:
        print "No clients connected"
        back_to_menu()

    selection = {}
    i = 1

    for client in clients:
        print "%d) %s" % (i, client)
        selection[i] = client
        i = i + 1

    select = raw_input('Select a client (0 for all):')
    flag = False

    if select.isdigit():
        filePath = raw_input('Source File: ')

        if not os.path.exists(filePath):
            print "Cannot locate file"
            transfer_file()

        fileSize = os.path.getsize(filePath)
        dest = raw_input('Destination path: ')

        fileData = open(filePath, 'rb')
        data = fileData.read(1024)

        if int(select) in selection:
            fileSend = clients[client]['socket'].send

        elif int(select) == 0:
            fileSend = clients[selection[1]]['socket'].sendall

        fileSend('%s "%s" "%d"\n' % ('FILE', dest, fileSize))
        time.sleep(1)

        while (data):

            fileSend(data)
            data = fileData.read(1024)

        fileSend('')
        fileData.close()

        while clients[client].recv(16):
            print clients[client].recv(16)

    else:
        flag = True

    if flag:
        raw_input('Invalid selection')
        transfer_file()

    back_to_menu()

def install_on_client ():
    clientsHelper('Install on client: ', 'INST', install_on_client)

def remove_on_client ():
    clientsHelper('Remove on client: ', 'RMOV', remove_on_client)

def clientsHelper(prompt, prefix, cb):

    clients = conns.getConnections()
    if clients.__len__() == 0:
        print "No clients connected"
        back_to_menu()

    selection = {}
    i = 1

    for client in clients:
        print "%d) %s" % (i, client)
        selection[i] = client
        i = i + 1

    select = raw_input('Select a client (0 for all):')
    flag = False

    if select.isdigit():
        args = raw_input('%s' % prompt)

        if int(select) in selection:
            selectedClient = clients[client]['socket']
            selectedClient.send('%s "%s"' % (prefix, args))

        elif int(select) == 0:
            selectedClient = clients[selection[1]]['socket']
            selectedClient.sendall('%s "%s"' % args)
        else:
            flag = True
    else:
        flag = True

    if flag:
        raw_input('Invalid selection')
        cb()

    back_to_menu()

def proccess_user_selection (option):

    user_select = {
        1: show_clients,
        2: send_commands,
        3: transfer_file,
        4: install_on_client,
        5: remove_on_client
    }

    if not option == '' and option.isdigit() and int(option) in user_select:
        invoke = user_select[int(option)]
        invoke()

    else:
        print "Invalid option"
        back_to_menu()

def back_to_menu ():
    raw_input('Press enter to contiue...')
    menu()

def menu ():

    print """
      1) Show all clients
      2) Send commands to all clients
      3) Transfer file to clients
      4) Install something on all clients
      5) Remove something from all clients
      """

    user_input = raw_input("-> ")

    proccess_user_selection(user_input)

def main ():

    global conns
    conns = Connections()
    server = Server('0.0.0.0', 1337)
    t = threading.Thread(target= server.listen)
    t.setDaemon(True)
    t.start()

    menu()

main()