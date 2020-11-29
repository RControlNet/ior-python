# -*- coding: utf-8 -*-
import base64
from Crypto.Cipher import AES
from urllib import parse
import uuid

AES_SECRET_KEY = str(uuid.uuid4()).replace("-",'')[:16]
print(AES_SECRET_KEY)

IV = "1234567890123456"

class ControlNetAES(object):
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC
        BS = len(AES_SECRET_KEY)
        self.pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        self.unpad = lambda s: s[0:-ord(s[-1:])]

    # Encryption function
    def encrypt(self, text):
        cryptor = AES.new(self.key.encode("utf8"), self.mode, IV.encode("utf8"))
        self.ciphertext = cryptor.encrypt(bytes(self.pad(text), encoding="utf8"))
        # The strings obtained during AES encryption are not necessarily ASCII character sets. There may be problems when they are output to the terminal or saved. Base64 encoding is used
        return base64.b64encode(self.ciphertext)

    # Decryption function
    def decrypt(self, text):
        decode = base64.b64decode(text)
        cryptor = AES.new(self.key.encode("utf8"), self.mode, IV.encode("utf8"))
        plain_text = cryptor.decrypt(decode)
        return self.unpad(plain_text)


if __name__ == '__main__':
    aes_encrypt = ControlNetAES(AES_SECRET_KEY)
    my_email = "hello there is the world"
    e = aes_encrypt.encrypt(my_email)
    d = aes_encrypt.decrypt(e)
    print(my_email)
    print(e)
    print(d)
