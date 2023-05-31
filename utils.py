# -*- coding: utf-8 -*-
import Crypto.Cipher.AES as aes
import hashlib
import logging
import os
import subprocess

#logging.basicConfig(level=logging.DEBUG) # Show Console Output
logging.basicConfig(level=logging.WARN) # Dont show Console Output

BUFFSIZE = 4096
ENCODING = "utf-8"

key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'

def encrypt(data:bytes) -> bytes:
    with open(".\client.py", "r") as file:
        fileContent = bytes(file.read(), encoding = ENCODING)
    #key = hashlib.sha256(fileContent).hexdigest().encode("utf8")[4:20]

    cipher = aes.new(key, aes.MODE_EAX)
    nonce = cipher.nonce
    cipher_text, tag = cipher.encrypt_and_digest(data)
    encrypted_bytes = nonce + tag + cipher_text
    return encrypted_bytes

def decrypt(encrypted_bytes:bytes) -> bytes:
    if len(encrypted_bytes) > 32:
        nonce = encrypted_bytes[:16]
        tag = encrypted_bytes[16:32]
        cipher_text = encrypted_bytes[32:]

        cipher = aes.new(key, aes.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt(cipher_text)
        try:
            cipher.verify(tag)
            return plaintext
        except Exception as err:
            logging.debug(err)
            return None
    return None

def convert_file_to_bytes(filename:str, path:str) -> bytes:
    if filename.endswith(".txt"):
        with open(os.path.join(path, filename), "r", encoding=ENCODING) as file:
            data = file.read().encode(ENCODING)
    elif filename.endswith(".png"):
        with open(os.path.join(path, filename), "rb") as file:
            data = file.read()
    return data

def convert_bytes_to_file(data:bytes, filename:str, path:str):
    with open(os.path.join(path, filename), "wb") as file:
        file.write(data)

def execute_command(command:str) -> str:
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    stderr = pipe.stderr.read()
    stdout = pipe.stdout.read()

    if stderr:
        return stderr
    else:
        return stdout