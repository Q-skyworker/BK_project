# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
from Crypto import Random
from common.log import logger

AES_KEY = '73f40f2c57eae727a4be171009cecf89'


def aes_encrypt(data):
    if data:
        bs = AES.block_size
        pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
        iv = Random.new().read(bs)
        cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
        data = cipher.encrypt(pad(data))
        data = iv + data
        return data.encode('base64')
    else:
        return ''


def aes_decrypt(data):
    try:
        data = data.decode('base64')
        bs = AES.block_size
        if len(data) <= bs:
            return True, data
        unpad = lambda s: s[0:-ord(s[-1])]
        iv = data[:bs]
        cipher = AES.new(AES_KEY, AES.MODE_CBC, iv)
        data = unpad(cipher.decrypt(data[bs:]))
        return True, data
    except Exception as e:
        logger.exception("aes_decrypt")
        return False, ""
