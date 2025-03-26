import winreg
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def load_signature_from_registry(section=r"SOFTWARE\Kravchenko", parameter="Signature"):
    """
    Зчитує інформацію з реєстру

    :param section: Шлях до секції реєстру
    :param parameter: Параметр з реєстру інформацію якого потрібно отримати
    :return: Інформація з реєстру або None, якщо виникла помилка
    """
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, section)
        signature, _ = winreg.QueryValueEx(reg_key, parameter)
        winreg.CloseKey(reg_key)
        return signature
    except Exception:
        return None

def verify_signature(public_key_pem: bytes, hashed_data):
    """
    Перевіряє підписані дані за допомогою публічного ключа

    :param public_key_pem: Публічний ключ
    :param hashed_data: Хешована інформація
    :return: True - якщо підпис дійсний, False - якщо підпис недійсний
    """
    public_key = serialization.load_pem_public_key(public_key_pem)
    signature = load_signature_from_registry()
    if not signature:
        return False

    try:
        public_key.verify(
            signature,
            hashed_data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

def write_to_registry(param_value, param_name='Signature', reg_path=r"SOFTWARE\Kravchenko"):
    """
    Записує інформацію у певний відділ реєстру, якщо відділ відсутній - створює його

    :param param_value: Інформація, яку потрібно записати
    :param param_name: Ім'я параметру реєстру куди заносяться дані
    :param reg_path: Шлях до секції реєстру
    :return:
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, param_name, 0, winreg.REG_BINARY, param_value)
    except FileNotFoundError:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            pass
        write_to_registry(param_value, param_name)

def sign_data(data: str, private_key) -> bytes:
    """
    Підписує хеш даних за допомогою приватного ключа

    :param data: Дані, які потрібно підписати
    :param private_key: Приватний ключ
    :return: Підписані дані
    """
    hash_object = hash_data(data)
    signature = private_key.sign(
        hash_object,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def keys_generation_data_signing(system_info):
    """
    Генерує ключі та підписує інформацію про систему

    :param system_info: Зібрана інформація про систему
    :return:
    """
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    write_to_registry(public_pem, "PublicKey")


    signature = sign_data(system_info, private_key)

    write_to_registry(signature)


def hash_data(data: str) -> bytes:
    """
    Хешує вхідні дані за допомогою SHA-256

    :param data: вхідні дані (plain text)
    :return: хеш вхідних даних
    """
    hash_object = hashlib.sha256(data.encode('utf-8'))
    return hash_object.digest()