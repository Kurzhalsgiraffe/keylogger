import Crypto.Cipher.AES as aes
import hashlib
import subprocess

def encrypt(filename:str):
    openFile = open(".\client.py", "r")
    fileContent = bytes(openFile.read(), encoding = "utf-8")
    #key = hashlib.sha256(fileContent).hexdigest().encode("utf8")[4:20]
    key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'
    cipher = aes.new(key, aes.MODE_EAX)
    nonce = cipher.nonce

    if filename.endswith(".txt"):
        with open(filename, "r", encoding="utf-8") as file:
            data = file.read().encode("utf-8")
    elif filename.endswith(".png"):
        with open(filename, "rb") as file:
            data = file.read()
    else:
        data = filename

    cipher_text, tag = cipher.encrypt_and_digest(data)
    return nonce + tag + cipher_text

def decrypt(cipher_text):
    key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'
    cipher = aes.new(key, aes.MODE_EAX, nonce = cipher_text[:16])
    plaintext = cipher.decrypt(cipher_text[32:])
    try:
        cipher.verify(cipher_text[16:32])
        return plaintext
    except Exception as e:
        print(e)
        return None

def execute_command(command):
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
    stderr = pipe.stderr.read()
    stdout = pipe.stdout.read()

    if stderr:
        return stderr
    else:
        return stdout
