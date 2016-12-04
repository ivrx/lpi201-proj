#!/usr/bin/python
import subprocess
import sys
import socket
import os.path

def runCmd(args):
    print "running command:", args

def falseCmd(args):
    print "Invalid command, args:", args

def fileCmd(data, dest):

    print "in get file", dest
    print data

def installCmd(args):
    print "install", args

def removeCmd(args):
    print "remove", args

def netcatCmd(args):
    print "netcat", args

def client(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
    except:
        print "Cannot connect"
        sys.exit()

    fileTransferFlag = False

    while True:
        data = s.recv(1024)

        if "FILE \"" in data:

            fileDest = data.split('"')[1]
            fileSize = data.split('"')[3]
            fileTransferFlag = True
            fileRecv = open(fileDest, 'wb')


        if fileTransferFlag:

            i = 1
            tmpSize = 0

            while data:

                data = s.recv(1024)

                fileRecv.write(data)
                tmpSize += i * 1024

                if tmpSize >= int(fileSize):

                    fileTransferFlag = False
                    fileRecv.close()

                    if int(os.path.getsize(fileDest)) == int(fileSize):
                        s.send('OK')
                        print "in OK"
                    else:
                        s.send('ERR')
                        print "in ERR"

        if not fileTransferFlag:

            prefix = data.split()[0]
            args = data.split('"')[1]


            case = {
                "EXEC": runCmd,
                "INST": installCmd,
                "RMOV": removeCmd,
                "NCAT": netcatCmd
            }

            if prefix in case:

                invoke = case.get(prefix, falseCmd)
                invoke(args)

def main ():

    client('127.0.0.1', 1337)

main()