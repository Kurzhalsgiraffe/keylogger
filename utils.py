import Crypto.Cipher.AES as aes
import hashlib

def encrypt(fileName):
    openFile = open(".\client.py", "r")
    fileContent = bytes(openFile.read(), encoding = "utf-8")
    #key = hashlib.sha256(fileContent).hexdigest().encode("utf8")[4:20]
    key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'
    cipher = aes.new(key, aes.MODE_EAX)
    nonce = cipher.nonce

    if(fileName[-4:] == ".txt"):
        file = open(fileName, "r")
        fileData = file.read().encode("ascii")
    elif(fileName[-4:] == ".png"):
        file = open(fileName, "rb")
        fileData = file.read()
    else:
        fileData = fileName

    cipherText, tag = cipher.encrypt_and_digest(fileData)
    return nonce + tag + cipherText

def decrypt(cipherText):
    key = b'\xe9\xcex8\x01\x98\xc5Z\xed\xd0F\xff\xff\xff\xff\xff'
    sNonce = cipherText[:16]
    sTag = cipherText[16:32]
    cipher = aes.new(key, aes.MODE_EAX, nonce = sNonce)
    plainText = cipher.decrypt(cipherText[32:])
    try:
        cipher.verify(sTag)
        return plainText
    except Exception as e:
        print(e)
        return None
