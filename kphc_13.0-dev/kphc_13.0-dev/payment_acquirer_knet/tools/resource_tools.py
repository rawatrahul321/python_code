from io import BytesIO
from zipfile import ZipFile

from Cryptodome.Cipher import DES, DES3
from jks import KeyStore
from lxml import etree


def _get_cipher(key: bytes):
    """Creates a new DES ECB cipher with given key."""
    # Our test key's all octets are same, this causes DES3's key to degenerate to single DES.
    #  PyCryptodome doesn't like this and raise exception in such a case.
    try:
        key = DES3.adjust_key_parity(key)
        cipher = DES3.new(key, DES3.MODE_ECB)
    except ValueError as exc:
        cipher = DES.new(key[:8], DES.MODE_ECB)
    return cipher


def _read_pgkey(ks_data: bytes, password: str) -> bytes:
    """Reads pgkey from keystore."""
    store = KeyStore.loads(ks_data, password)
    return store.entries["pgkey"].key


def _decrypt_cgn(cgn_data: bytes, key: bytes) -> bytes:
    """Decrypts the given .cgn data and returns the content."""
    cipher = _get_cipher(key)
    dec_data = cipher.decrypt(cgn_data)

    return dec_data


def _get_alias_xml(zip_data: bytes, key: bytes, alias: str = None) -> bytes:
    """Returns decrypted xml data from given zip_data with name alias."""
    zip_file = ZipFile(BytesIO(zip_data))
    file_name = alias + ".xml" if alias else zip_file.namelist()[0]
    enc_data = zip_file.read(file_name)
    dec_data = _get_cipher(key).decrypt(enc_data)
    dec_data = dec_data.replace(b"\x02", b"")

    return dec_data


def parse_resource(resource_data: bytes, ks_data: bytes, ks_password: str, alias: str = None) -> dict:
    """Parses given resources data and returns a dict containing the data stored in the file."""
    vals = {}
    # Read key from keystore.
    key = _read_pgkey(ks_data, ks_password)
    cgn = _decrypt_cgn(resource_data, key)
    xml = _get_alias_xml(cgn, key, alias)

    for entry in etree.fromstring(xml):
        vals[entry.tag] = entry.text
    return vals


def parse_resource_file(resource_path: str, ks_path: str, ks_password: str, alias: str = None) -> dict:
    """Convenience function to ease reading resource file. Simple wrapper around parse_resources(). """
    with open(ks_path, "rb") as f:
        ks_data = f.read()
    with open(resource_path, "rb") as f:
        resource_data = f.read()

    return parse_resource(resource_data, ks_data, ks_password, alias)
