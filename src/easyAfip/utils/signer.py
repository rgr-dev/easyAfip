from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives.serialization.pkcs7 import PKCS7SignatureBuilder, PKCS7Options
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.backends import default_backend

class Signer:
    def __init__(self, pem, key):
        self.pem = pem
        self.key = key

    def sign_cms(self, data):
        private_key = load_pem_private_key(self.key, password=None, backend=default_backend())
        certificate = load_pem_x509_certificate(self.pem, backend=default_backend())

        builder = PKCS7SignatureBuilder()
        builder = builder.set_data(data)
        builder = builder.add_signer(certificate, private_key, hashes.SHA256())
        builder = builder.sign(encoding=Encoding.PEM, options=[])
        return builder