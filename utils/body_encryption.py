import base64
import os
from dotenv import load_dotenv
from Crypto.Cipher import AES

load_dotenv()


class AESCipher(object):
    def __init__(self):
        self.bs = AES.block_size
        self.key = os.environ.get("AES256_KEY").encode()
        self.iv = os.environ.get("AES256_IV").encode()

    def encrypt(self, raw: bytes):
        padded = self._pad(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return base64.b64encode(self.iv + cipher.encrypt(padded))

    def decrypt(self, enc: bytes):
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        return self._unpad(cipher.decrypt(enc[self.bs :])).decode("utf-8")

    def _pad(self, s):
        pad_size = self.bs - len(s) % self.bs
        pad = bytes([pad_size] * pad_size)
        return s + pad

    def _unpad(self, s: bytes):
        padding_size = s[-1]
        if padding_size < 1 or padding_size > self.bs:
            # 패딩 크기가 유효하지 않은 경우 에러를 발생시킵니다.
            raise ValueError("Invalid padding size.")
        padding_start = len(s) - padding_size
        for i in range(padding_start, len(s)):
            if s[i] != padding_size:
                # 패딩 값이 유효하지 않은 경우 에러를 발생시킵니다.
                raise ValueError("Invalid padding.")
        return s[:padding_start]
