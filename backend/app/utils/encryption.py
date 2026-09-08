from cryptography.fernet import Fernet

from backend.app.core.config import settings


class CredentialEncryption:
    """
    Encrypts and decrypts sensitive network credentials.

    The encryption key is loaded from the environment and must
    never be hardcoded or exposed through API responses or logs.
    """

    def __init__(self, key: str):
        self.fernet = Fernet(key.encode())

    def encrypt(self, value: str) -> str:
        """
        Encrypt a plaintext credential.
        """

        return self.fernet.encrypt(
            value.encode()
        ).decode()

    def decrypt(self, value: str) -> str:
        """
        Decrypt an encrypted credential.
        """

        return self.fernet.decrypt(
            value.encode()
        ).decode()


credential_encryption = CredentialEncryption(
    settings.NETWORK_CREDENTIAL_ENCRYPTION_KEY
)