import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.security import (
    DataMaskingService, ReversibleEncryption,
    hash_password, verify_password, default_masking_service
)


class TestSecurity(unittest.TestCase):

    def test_mask_email(self):
        svc = DataMaskingService()
        masked = svc.mask_text("contact user@example.com please")
        self.assertIn("****@", masked)
        self.assertNotIn("user@", masked)

    def test_mask_phone(self):
        svc = DataMaskingService()
        masked = svc.mask_text("call 415-555-1234 now")
        self.assertIn("***", masked)
        self.assertNotEqual(masked, "call 415-555-1234 now")

    def test_mask_credit_card(self):
        svc = DataMaskingService()
        masked = svc.mask_text("card 4111111111111111 charged")
        self.assertIn("****-****-****-", masked)
        self.assertNotIn("4111111111111111", masked)

    def test_mask_dict(self):
        svc = DataMaskingService()
        data = {"password": "secret123", "name": "Alice", "email": "alice@example.com"}
        masked = svc.mask_dict(data)
        self.assertNotEqual(masked["password"], "secret123")
        self.assertEqual(masked["name"], "Alice")

    def test_context_levels(self):
        svc_log = DataMaskingService(context_level="LOGGING")
        svc_analytics = DataMaskingService(context_level="ANALYTICS")
        text = "user@test.com owes 4111111111111111"
        masked_log = svc_log.mask_text(text)
        masked_analytics = svc_analytics.mask_text(text)
        self.assertIn("****@", masked_log)
        self.assertIn("****-****-****-", masked_analytics)

    def test_encryption_roundtrip(self):
        enc = ReversibleEncryption(key=b"testkey_32bytes_long_enough!!!")
        plaintext = "hello world"
        ciphertext = enc.encrypt(plaintext)
        self.assertIsInstance(ciphertext, str)
        decrypted = enc.decrypt(ciphertext)
        self.assertEqual(decrypted, plaintext)

    def test_key_rotation(self):
        old_key = b"old_key_32bytes_long_enough!!!"
        new_key = b"new_key_32bytes_long_enough!!!"
        enc = ReversibleEncryption(key=old_key)
        values = ["secret1", "secret2"]
        encrypted = [enc.encrypt(v) for v in values]
        rotated = enc.rotate_key(new_key, encrypted)
        self.assertEqual(len(rotated), 2)
        enc._key = new_key
        for orig, ct in zip(values, rotated):
            self.assertEqual(enc.decrypt(ct), orig)

    def test_password_hashing(self):
        pw = "mypassword123"
        h, s = hash_password(pw)
        self.assertTrue(verify_password(pw, h, s))
        self.assertFalse(verify_password("wrong", h, s))

    def test_custom_iterations(self):
        pw = "testpw"
        h, s = hash_password(pw, iterations=1000)
        self.assertTrue(verify_password(pw, h, s, iterations=1000))

    def test_default_service(self):
        self.assertIsNotNone(default_masking_service)
        self.assertIsInstance(default_masking_service, DataMaskingService)


if __name__ == '__main__':
    unittest.main()
