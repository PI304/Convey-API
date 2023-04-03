import base64
import os
from dotenv import load_dotenv
from Crypto.Cipher import AES

load_dotenv()


class AESCipher(object):
    def __init__(self):
        self.bs = AES.block_size
        self.key = bytes(os.environ.get("AES256_KEY"), "utf-8")
        self.iv = bytes(os.environ.get("AES256_IV"), "utf-8")

    def encrypt(self, raw):
        raw = self._pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(self.iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[: -ord(s[len(s) - 1 :])]
