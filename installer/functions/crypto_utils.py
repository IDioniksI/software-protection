from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA256

def derive_key(password: str, salt: bytes, key_len=32) -> bytes:
    return PBKDF2(password, salt, dkLen=key_len, count=100_000, hmac_hash_module=SHA256)

def encrypt_data_chacha(data: bytes, password: str) -> bytes:
    salt = get_random_bytes(16)
    key = derive_key(password, salt, key_len=32)
    cipher = ChaCha20.new(key=key)
    ciphertext = cipher.encrypt(data)
    return salt + cipher.nonce + ciphertext

def decrypt_data_chacha(data: bytes, password: str) -> bytes:
    salt = data[:16]
    nonce = data[16:24]
    ciphertext = data[24:]
    key = derive_key(password, salt, key_len=32)
    cipher = ChaCha20.new(key=key, nonce=nonce)
    return cipher.decrypt(ciphertext)

# from Crypto.Cipher import AES
# from Crypto.Random import get_random_bytes
# from Crypto.Protocol.KDF import PBKDF2
# from Crypto.Hash import SHA256
#
# def derive_key(password: str, salt: bytes, key_len=32) -> bytes:
#     return PBKDF2(password, salt, dkLen=key_len, count=100_000, hmac_hash_module=SHA256)
#
# def encrypt_data_aes_ctr(data: bytes, password: str) -> bytes:
#     salt = get_random_bytes(16)
#     nonce = get_random_bytes(8)
#     key = derive_key(password, salt)
#     cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
#     encrypted = cipher.encrypt(data)
#     return salt + nonce + encrypted  # зберігаємо salt і nonce на початку
#
# def decrypt_data_aes_ctr(data: bytes, password: str) -> bytes:
#     salt = data[:16]
#     nonce = data[16:24]
#     ciphertext = data[24:]
#     key = derive_key(password, salt)
#     cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
#     return cipher.decrypt(ciphertext)

