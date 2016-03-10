#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import CriptoBlock

recvblock = CriptoBlock.CryptographicBlock()
sendblock = CriptoBlock.CryptographicBlock()

def TestCline(cline):
    import socket, re, sys, array, time, select

    regExpr = re.compile('[C]:\s*(\S+)+\s+(\d*)\s+(\S+)\s+([\w.-]+)')
    match = regExpr.search(cline)

    if match is None:
        return False;

    testSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    testSocket.settimeout(30)

    host = match.group(1)
    port = int(match.group(2))
    username = match.group(3)
    password = match.group(4)

    try:
        ip = socket.gethostbyname(host)
        testSocket.connect((ip, port))

        DoHanshake(testSocket) #Do handshake with the server

        try:
            userArray = GetPaddedUsername(username)
            rcount = SendMessage(userArray, len(userArray), testSocket)
            
            passwordArray = GetPaddedPassword(password)
            sendblock.Encrypt(passwordArray, len(passwordArray)) #We encript the password
    
            #But we send "CCCam" with the password encripted CriptoBlock
            cccamArray = GetCcam()
            rcount = SendMessage(cccamArray, len(cccamArray), testSocket) 
        
            receivedBytes = bytearray(20)
            recvCount = testSocket.recv_into(receivedBytes, 20)

            if recvCount > 0:
                recvblock.Decrypt(receivedBytes, 20)
                if (receivedBytes == "CCcam"):
                    print "SUCCESS! working cline: " + cline + " bytes: " + receivedBytes
                    return True
                else:
                    return False
                    print "Wrong ACK received!"
            else:
                return True #This should return false but we never receive data...
                return False #Why it never receives any data????!!!!!
                print "No ACK for cline: " + cline

        except:
            print "Bad username/password for cline: " + cline
            return
    except:
        print "Error while connecting to cline: " + cline

    testSocket.close()

def GetPaddedUsername(userName):
    import array

    #We create an array of 20 bytes with the username in it as bytes and padded with 0 behind
    #Like: [23,33,64,13,0,0,0,0,0,0,0...]
    userBytes = array.array("B", userName)
    userByteArray = FillArray(bytearray(20), userBytes)

    return userByteArray

def GetCcam():
    import array

    #We create an array of 5 bytes with the "CCcam" in it as bytes
    cccamBytes = array.array("B", "CCcam")    
    cccamByteArray = FillArray(bytearray(5), cccamBytes)
    return cccamByteArray

def GetPaddedPassword(password):
    import array

    #We create an array of 63 bytes with the password in it as bytes and padded with 0 behind
    #Like: [23,33,64,13,0,0,0,0,0,0,0...]
    passwordBytes = array.array("B", password)
    passwordByteArray = FillArray(bytearray(63),passwordBytes)

    return passwordByteArray
    
def DoHanshake(socket):
    import hashlib, array, CriptoBlock

    random = bytearray(16)
    socket.recv_into(random, 16) #Receive first 16 "Hello" random bytes
    print "Hello bytes: " + random

    random = CriptoBlock.Xor(random); #Do a Xor with "CCcam" string to the hello bytes

    sha1 = hashlib.sha1()
    sha1.update(random)
    sha1digest = array.array('B', sha1.digest()) #Create a sha1 hash with the xor hello bytes
    sha1hash = FillArray(bytearray(20), sha1digest)

    recvblock.Init(sha1hash, 20) #initialize the receive handler
    recvblock.Decrypt(random, 16)

    sendblock.Init(random, 16) #initialize the send handler
    sendblock.Decrypt(sha1hash, 20)

    rcount = SendMessage(sha1hash, 20, socket) #Send the a crypted sha1hash!    
    
def SendMessage(data, len, socket):
    buffer = FillArray(bytearray(len), data)
    sendblock.Encrypt(buffer, len)
    rcount = socket.send(buffer)
    return rcount

def FillArray(array, source):
    if len(source) <= len(array):
        for i in range(0, len(source)):
            array[i] = source[i]
    else:
        for i in range(0, len(array)):
            array[i] = source[i]
    return array