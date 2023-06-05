# -*- coding: utf-8 -*-
import Crypto.Cipher.AES as aes
import hashlib
import logging
import requests

logging.basicConfig(level=logging.INFO) # Show Console Output
#logging.basicConfig(level=logging.WARN) # Dont show Console Output

BUFFSIZE = 4096
ENCODING = "utf-8"
KEY = None
URL = "https://example.com"

def encrypt(data:bytes) -> bytes:
    if not KEY:
        generate_key()

    with open(".\client.py", "r") as file:
        file_content = bytes(file.read(), encoding = ENCODING)
    #key = hashlib.sha256(file_content).hexdigest().encode("utf8")[4:20]

    cipher = aes.new(KEY, aes.MODE_EAX)
    nonce = cipher.nonce
    cipher_text, tag = cipher.encrypt_and_digest(data)
    encrypted_bytes = nonce + tag + cipher_text
    return encrypted_bytes

def decrypt(encrypted_bytes:bytes) -> bytes:
    if not KEY:
        generate_key()

    if len(encrypted_bytes) > 32:
        nonce = encrypted_bytes[:16]
        tag = encrypted_bytes[16:32]
        cipher_text = encrypted_bytes[32:]

        cipher = aes.new(KEY, aes.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt(cipher_text)
        try:
            cipher.verify(tag)
            return plaintext
        except Exception as err:
            logging.debug(err)
            return None

def generate_key():
    global KEY
    page = requests.get(URL)
    page_in_bytes = bytes(page.text, encoding=ENCODING)
    KEY = hashlib.sha256(page_in_bytes).hexdigest().encode("utf8")[4:20]
