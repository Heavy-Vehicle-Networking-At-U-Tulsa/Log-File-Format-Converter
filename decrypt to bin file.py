#!/usr/bin/python3
import socket
import sys
import uuid
import struct
from Crypto.Cipher import AES
from tkinter import *
from tkinter.filedialog import *


key_byte =[0x04,0x1E,0xFE,0x74,0x57,0xFB,0xF2,0xFC,0x76,0x20,0xC2,0x2B,0x8E,0xE8,0x9B,0x65]
iv_byte = [0x89,0xD5,0x19,0x0D,0x36,0x71,0xDE,0x92,0x61,0xFB,0xE4,0x23,0x99,0xAF,0x7C,0x40]
key_convert = ("".join(["{:02X}".format(b) for b in key_byte]))
key_string=(bytes.fromhex(key_convert))
iv_convert = ("".join(["{:02X}".format(b) for b in iv_byte]))
iv_string=(bytes.fromhex(iv_convert))

decipher = AES.new(key_string,AES.MODE_CBC,iv_string)



LOG_FILE_NAME = askopenfilename()
DECRYPT_FILE_NAME = 'logfile_{}.bin'.format(uuid.uuid4()) #uuid4 generates a random universally unique identifier
Buffer_size = 512


message_list = []

fileLocation = 0
file_size = os.path.getsize(LOG_FILE_NAME)
with open (DECRYPT_FILE_NAME, 'wb') as decrypt_file:
    with open (LOG_FILE_NAME, 'rb') as file:
        while(fileLocation<file_size):
            
            block =decipher.decrypt(file.read(512)) #read every 512 bytes
            decrypt_file.write(block)
            fileLocation+=512

sys.exit()