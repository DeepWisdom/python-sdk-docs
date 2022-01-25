from Crypto.Cipher import AES
import base64

from Crypto.Util.Padding import pad


class AesCrypt:
    def __init__(self, model, iv, encode_, key='databaseloginpwd'):
        self.encrypt_text = ''
        self.decrypt_text = ''
        self.encode_ = encode_
        self.model = {'ECB': AES.MODE_ECB, 'CBC': AES.MODE_CBC}[model]
        self.key = self.add_16(key)
        if model == 'ECB':
            self.aes = AES.new(self.key, self.model)  # 创建一个aes对象
        elif model == 'CBC':
            self.aes = AES.new(self.key, self.model, iv)  # 创建一个aes对象

        # 这里的密钥长度必须是16、24或32，目前16位的就够用了

    def add_16(self, par):
        par = par.encode(self.encode_)
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    # 加密
    def aesencrypt(self, text):
        text = pad(text.encode('utf-8'), AES.block_size, style='pkcs7')
        self.encrypt_text = self.aes.encrypt(text)
        return base64.encodebytes(self.encrypt_text).decode().strip()

    # 解密
    def aesdecrypt(self, text):
        text = base64.decodebytes(text.encode(self.encode_))
        self.decrypt_text = self.aes.decrypt(text)
        return self.decrypt_text.decode(self.encode_).strip("\x0c").strip("\x10").strip('\0').strip("\n")