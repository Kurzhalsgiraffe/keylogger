import Crypto.Cipher.AES as aes
import hashlib
import os
import subprocess

BUFFSIZE = 4096

key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'

def encrypt(data:bytes) -> bytes:
    openFile = open(".\client.py", "r")
    fileContent = bytes(openFile.read(), encoding = "utf-8")
    #key = hashlib.sha256(fileContent).hexdigest().encode("utf8")[4:20]

    cipher = aes.new(key, aes.MODE_EAX)
    nonce = cipher.nonce
    cipher_text, tag = cipher.encrypt_and_digest(data)
    encrypted_bytes = nonce + tag + cipher_text
    return encrypted_bytes

def decrypt(encrypted_bytes:bytes) -> bytes:
    nonce = encrypted_bytes[:16]
    tag = encrypted_bytes[16:32]
    cipher_text = encrypted_bytes[32:]

    cipher = aes.new(key, aes.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(cipher_text)
    try:
        cipher.verify(tag)
        return plaintext
    except Exception as e:
        print(e)
        return None, None

def convert_file_to_bytes(filename:str) -> bytes:
    if filename.endswith(".txt"):
        with open(filename, "r", encoding="utf-8") as file:
            data = file.read().encode("utf-8")
    elif filename.endswith(".png"):
        with open(filename, "rb") as file:
            data = file.read()
    return data

def convert_bytes_to_file(data:bytes, dtype:str, path:str):
    file_basename = str(len(os.listdir(path)))
    filename = file_basename + "." + dtype
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