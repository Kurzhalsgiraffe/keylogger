import Crypto.Cipher.AES as aes
import hashlib
import subprocess

key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'

def encrypt(data:bytes, ftype:str) -> bytes:
    if ftype not in ["msg", "png", "txt"]:
        return None
    openFile = open(".\client.py", "r")
    fileContent = bytes(openFile.read(), encoding = "utf-8")
    #key = hashlib.sha256(fileContent).hexdigest().encode("utf8")[4:20]

    cipher = aes.new(key, aes.MODE_EAX)
    nonce = cipher.nonce

    cipher_text, tag = cipher.encrypt_and_digest(data)
    return nonce + tag + ftype.encode("utf-8") + cipher_text

def decrypt(encrypted_bytes:bytes):
    nonce = encrypted_bytes[:16]
    tag = encrypted_bytes[16:32]
    ftype = encrypted_bytes[32:35].decode("utf-8")
    cipher_text = encrypted_bytes[35:]

    cipher = aes.new(key, aes.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(cipher_text)
    try:
        cipher.verify(tag)
        return plaintext
    except Exception as e:
        print(e)
        return None

def convert_file_to_bytes(filename:str) -> bytes:
    if filename.endswith(".txt"):
        with open(filename, "r", encoding="utf-8") as file:
            data = file.read().encode("utf-8")
    elif filename.endswith(".png"):
        with open(filename, "rb") as file:
            data = file.read()
    return data

def execute_command(command):
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    stderr = pipe.stderr.read()
    stdout = pipe.stdout.read()

    if stderr:
        return stderr
    else:
        return stdout