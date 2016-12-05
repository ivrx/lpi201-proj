#!/usr/bin/python
import subprocess
import sys
import socket
import os.path


def runCmd(args):
    s = args["socket"]
    cmd = args["args"]

    output = processCmd(cmd)
    s.send(output)


def installCmd(args):
    s = args["socket"]
    toInstall = args["args"]

    output = processCmd('apt-get install -y %s' % toInstall)
    s.send(output)


def fileCmd(args):
    print "print in file transfer"

    s = args["socket"]
    dest = args["dest"]
    size = args["size"]
    bufferSize = 1024
    fileRecv = open(dest, 'wb')
    tmpSize = 0

    while True:

        data = s.recv(bufferSize)
        fileRecv.write(data)
        tmpSize += bufferSize

        print "%d / %d" % (tmpSize, int(size))
        print os.path.getsize(dest)

        if tmpSize >= int(size):

            print "data received, closing file"

            fileRecv.close()

            if int(os.path.getsize(dest)) == int(size):
                s.send('OK')
                print "in OK"
                break
            else:
                s.send('ERR')
                print "in ERR"
                break


def removeCmd(args):
    s = args["socket"]
    toRemove = args["args"]

    output = processCmd('apt-get remove -y %s' % toRemove)
    s.send(output)

def shellCmd(args):
    # TODO: improve shell this one sucks

    s = args["socket"]
    port = int(args["args"])
    shellSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    shellSocket.bind(('0.0.0.0', int(port)))
    shellSocket.listen(1)
    conn, addr = shellSocket.accept()

    while True:
        cmd = conn.recv(1024)

        if cmd:
            ps = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)

            if ps:
                out = str(ps.stdout.read())
                conn.send(out)

            else:
                err = str(ps.stderr.read())
                conn.send(err)

def falseCmd(args):
    cmd = args["args"]
    print "Invalid command, args:", cmd

def processCmd(cmd):
    cmdSplit = cmd.split()
    errFlag = False

    try:
        call = subprocess.Popen(cmdSplit, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
    except:
        call = subprocess.CalledProcessError.message
        errFlag = True

    if errFlag:
        return 'failure\n\n%s' % str(call)

    else:
        call.wait()
        out, err = call.communicate()

        if call.returncode == 0:
            return 'success\n\n%s' % out

        elif call.returncode == 1:

            return 'failure\n\n%s' % out

        else:
            assert call.returncode > 1
            return 'failure\n\n%r' % (err,)

def client(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
    except:
        print "Cannot connect"
        sys.exit()

    # main loop:

    while True:
        data = s.recv(1024)

        if "FILE \"" in data:

            fileDest = data.split('"')[1]
            fileSize = data.split('"')[3]

            args = {
                "socket": s,
                "dest": fileDest,
                "size": fileSize
            }

            fileCmd(args)

        else:

            print data
            prefix = data.split()[0]
            args = {"args": data.split('"')[1], "socket": s}

            case = {
                "EXEC": runCmd,
                "INST": installCmd,
                "RMOV": removeCmd,
                "SHEL": shellCmd
            }

            if prefix in case:
                invoke = case.get(prefix, falseCmd)
                invoke(args)


def main():
    client('127.0.0.1', 1337)


main()
