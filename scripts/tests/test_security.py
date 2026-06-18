"""AI Agent Infra v3.7.0 - PG Community Edition - Security Module Tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.security import (
    DataMaskingService, ReversibleEncryption,
    hash_password, verify_password,
)


def test_data_masking_pii():
    svc = DataMaskingService("LOGGING")
    result = svc.mask_text("Contact user@example.com for details")
    assert "****@example.com" in result
    assert "user@" not in result

    result2 = svc.mask_text("Card 4111111111111111 charged")
    assert "****-****-****-1111" in result2

    result3 = svc.mask_text("SSN 123-45-6789 on file")
    assert "***-**-6789" in result3
    print("PASS: test_data_masking_pii")


def test_data_masking_context_levels():
    svc_logging = DataMaskingService("LOGGING")
    text_with_ip = "Server at 192.168.1.100 responded"
    masked_logging = svc_logging.mask_text(text_with_ip)
    assert "192.168.1.100" in masked_logging

    svc_debugging = DataMaskingService("DEBUGGING")
    masked_debug = svc_debugging.mask_text(text_with_ip)
    assert "192.168.1.100" not in masked_debug or "***" in masked_debug

    svc_analytics = DataMaskingService("ANALYTICS")
    result = svc_analytics.mask_text("Email test@domain.com card 4111111111111111")
    assert "****-****-****-1111" in result
    print("PASS: test_data_masking_context_levels")


def test_hash_verify_password():
    pw = "MySecurePassword123!"
    hash_val, salt = hash_password(pw)
    assert verify_password(pw, hash_val, salt)
    assert not verify_password("wrong_password", hash_val, salt)
    print("PASS: test_hash_verify_password")


def test_reversible_encryption():
    enc = ReversibleEncryption()
    plaintext = "Hello, PostgreSQL! This is a secret message."
    ciphertext = enc.encrypt(plaintext)
    decrypted = enc.decrypt(ciphertext)
    assert decrypted == plaintext
    print("PASS: test_reversible_encryption")


def test_mask_empty_string():
    svc = DataMaskingService("LOGGING")
    result = svc.mask_text("")
    assert result == ""
    result2 = svc.mask_text(None)
    assert result2 is None
    print("PASS: test_mask_empty_string")


def run_all():
    passed = 0
    failed = 0
    for test_fn in [
        test_data_masking_pii,
        test_data_masking_context_levels,
        test_hash_verify_password,
        test_reversible_encryption,
        test_mask_empty_string,
    ]:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test_fn.__name__} - {e}")
            failed += 1

    print(f"\nSecurity Tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
