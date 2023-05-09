from socket import socket
import Crypto.Cipher.AES as aes
import os

key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'

def decryption(cipherText):
    fileCounter = 1
    message = False
    sNonce = cipherText[:16]
    sTag = cipherText[16:32]
    cipher = aes.new(key, aes.MODE_EAX, nonce = sNonce)
    plainText = cipher.decrypt(cipherText[32:])
    if(plainText[:5] == b'\xff\xd8\xff\xe0\x00'):
        for i in os.listdir("."):
            fileCounter = fileCounter + 1
        newFile = str(fileCounter)+".jpg"
    elif(plainText[:5] == "Foreg"):
        for i in os.listdir("."):
            fileCounter = fileCounter + 1
        newFile = str(fileCounter)+".txt"
    else:
        message = True

    if message:
        try:
            cipher.verify(sTag)
            return plainText
        except:
            return "Message corrupted."
    else:
        try:
            cipher.verify(sTag)
            file = open(newFile, "wb")
            file.write(plainText)
            return "New file was added."
        except:
            return "Message corrupted."

host = "127.0.0.1"
port = 1005

sock = socket()
sock.bind((host, port))

sock.listen(5)  # listen for client connection. The number stands for: number of unaccepted connections that the system will allow before refusing new connections
conn, addr = sock.accept()  # Establish connection with client. conn: new socket object used to send and receive data. addr address bound to the socket of the client.
print('Got connection from', addr)


while True:
    inpt = input("Enter command:")
    conn.sendall(bytes(inpt, "ascii"))
    recv = decryption(conn.recv(1024))  #Data recieved from the socket. 1024 is the maximum amount of data to be received at once
    if recv:
        recv = str(recv)[2:-1]
        if(recv == "terminating"):
            print("Terminated client. Good bye!")
            break
        else:
            print(recv)

conn.close()
print("Connection closed.")