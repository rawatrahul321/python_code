from Cryptodome.Cipher import AES

BLOCK_SIZE = 16


def _pad_block(data: bytes, boundary: int = BLOCK_SIZE) -> bytes:
    """Pads given data to boundary size according to PKCS #5."""
    diff = boundary - len(data) % boundary
    return data + diff * bytes((diff, ))


def _unpad_block(data: bytes) -> bytes:
    """Removes PKCS #5 padding from data."""
    pad_length = data[-1]
    return data[:-pad_length]


def encrypt_data(data: str, key: str) -> str:
    """Encrypts given data and returns as hex-encoded string."""
    key = key.encode("UTF-8")
    data = _pad_block(data.encode("UTF-8"))

    # KNET uses key as IV.
    cipher = AES.new(key, AES.MODE_CBC, key)
    enc_data = cipher.encrypt(data)
    enc_data = enc_data.hex()

    return enc_data


def decrypt_data(hex_data: str, key: str) -> str:
    """Decrypts given hex-encoded encrypted data and returns plaintext."""
    key = key.encode("UTF-8")
    cipher = AES.new(key, AES.MODE_CBC, key)
    dec_data = cipher.decrypt(bytes.fromhex(hex_data))
    dec_data = _unpad_block(dec_data)

    return dec_data.decode("UTF-8")

