"""PostgreSQL Memory System v2.3.1 - Security Module Tests"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.security import (
    DataMaskingService, ReversibleEncryption,
    hash_password, verify_password,
)

_passed = 0
_failed = 0


def _record(ok):
    global _passed, _failed
    if ok:
        _passed += 1
    else:
        _failed += 1


def test_mask_text_email():
    try:
        service = DataMaskingService(context_level="LOGGING")
        text = "My email is user@example.com and my phone is 123-456-7890"
        masked = service.mask_text(text)
        ok = "user@example.com" not in masked and "123-456-7890" not in masked
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_mask_text_email: " + status)
    return ok


def test_mask_text_credit_card():
    try:
        service = DataMaskingService(context_level="LOGGING")
        text = "Card number 4111111111111111 charged"
        masked = service.mask_text(text)
        ok = "4111111111111111" not in masked
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_mask_text_credit_card: " + status)
    return ok


def test_mask_text_ssn():
    try:
        service = DataMaskingService(context_level="LOGGING")
        text = "SSN: 123-45-6789 on file"
        masked = service.mask_text(text)
        ok = "123-45-6789" not in masked
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_mask_text_ssn: " + status)
    return ok


def test_mask_text_jwt():
    try:
        service = DataMaskingService(context_level="LOGGING")
        text = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123def456ghi789"
        masked = service.mask_text(text)
        ok = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123def456ghi789" not in masked
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_mask_text_jwt: " + status)
    return ok


def test_mask_text_empty():
    try:
        service = DataMaskingService(context_level="LOGGING")
        ok = service.mask_text("") == ""
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_mask_text_empty: " + status)
    return ok


def test_mask_dict():
    try:
        service = DataMaskingService(context_level="LOGGING")
        data = {"password": "secret123", "description": "visible", "email": "user@example.com"}
        masked = service.mask_dict(data)
        ok = masked["description"] == "visible" and "secret123" not in str(masked.get("password", ""))
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_mask_dict: " + status)
    return ok


def test_mask_dict_nested():
    try:
        service = DataMaskingService(context_level="LOGGING")
        data = {"config": {"token": "abc123secret456", "name": "app"}}
        masked = service.mask_dict(data)
        ok = "abc123secret456" not in str(masked.get("config", {}).get("token", ""))
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_mask_dict_nested: " + status)
    return ok


def test_mask_json():
    try:
        service = DataMaskingService(context_level="LOGGING")
        import json
        json_str = json.dumps({"api_key": "secretkey123456789", "value": 42})
        masked = service.mask_json(json_str)
        ok = "secretkey123456789" not in masked
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_mask_json: " + status)
    return ok


def test_mask_json_invalid():
    try:
        service = DataMaskingService(context_level="LOGGING")
        result = service.mask_json("not valid json {")
        ok = isinstance(result, str)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_mask_json_invalid: " + status)
    return ok


def test_context_level_analytics():
    try:
        service = DataMaskingService(context_level="ANALYTICS")
        text = "Card 4111111111111111 and SSN 123-45-6789"
        masked = service.mask_text(text)
        ok = "4111111111111111" not in masked and "123-45-6789" not in masked
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_context_level_analytics: " + status)
    return ok


def test_context_level_debugging():
    try:
        service = DataMaskingService(context_level="DEBUGGING")
        text = "IP 10.0.0.1 connected"
        masked = service.mask_text(text)
        ok = "10.0.0.1" not in masked
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_context_level_debugging: " + status)
    return ok


def test_encryption_roundtrip():
    try:
        enc = ReversibleEncryption()
        plaintext = "sensitive data for encryption test"
        ciphertext = enc.encrypt(plaintext)
        decrypted = enc.decrypt(ciphertext)
        ok = decrypted == plaintext and ciphertext != plaintext
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_encryption_roundtrip: " + status)
    return ok


def test_encryption_different_keys():
    try:
        enc1 = ReversibleEncryption(key=b"a" * 32)
        enc2 = ReversibleEncryption(key=b"b" * 32)
        ciphertext = enc1.encrypt("test data")
        decrypted = enc1.decrypt(ciphertext)
        ok = decrypted == "test data"
        try:
            enc2.decrypt(ciphertext)
            ok = False
        except Exception:
            pass
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_encryption_different_keys: " + status)
    return ok


def test_key_rotation():
    try:
        old_key = os.urandom(32)
        enc = ReversibleEncryption(key=old_key)
        plaintext = "data before rotation"
        ciphertext = enc.encrypt(plaintext)
        new_key = os.urandom(32)
        rotated = enc.rotate_key(new_key, [ciphertext])
        ok = len(rotated) == 1
        enc2 = ReversibleEncryption(key=new_key)
        decrypted = enc2.decrypt(rotated[0])
        ok = ok and decrypted == plaintext
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_key_rotation: " + status)
    return ok


def test_password_hash_and_verify():
    try:
        password = "test_password_123"
        stored_hash, salt_hex = hash_password(password)
        ok = stored_hash != password and verify_password(password, stored_hash, salt_hex)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_password_hash_and_verify: " + status)
    return ok


def test_password_verify_wrong():
    try:
        stored_hash, salt_hex = hash_password("correct_password")
        ok = not verify_password("wrong_password", stored_hash, salt_hex)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_password_verify_wrong: " + status)
    return ok


def test_password_custom_iterations():
    try:
        stored_hash, salt_hex = hash_password("fast_hash", iterations=1000)
        ok = verify_password("fast_hash", stored_hash, salt_hex, iterations=1000)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_password_custom_iterations: " + status)
    return ok


def test_password_custom_salt():
    try:
        salt = os.urandom(16)
        stored_hash, salt_hex = hash_password("salted_pw", salt=salt)
        ok = salt_hex == salt.hex() and verify_password("salted_pw", stored_hash, salt_hex)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_password_custom_salt: " + status)
    return ok


def test_masking_order():
    try:
        service = DataMaskingService(context_level="LOGGING")
        text = "SSN: 123-45-6789, Email: a@b.com, Phone: 555-000-1234"
        masked = service.mask_text(text)
        ssn_gone = "123-45-6789" not in masked
        email_gone = "a@b.com" not in masked
        phone_gone = "555-000-1234" not in masked
        ok = ssn_gone and email_gone and phone_gone
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_masking_order: " + status)
    return ok


def run_all():
    tests = [
        test_mask_text_email, test_mask_text_credit_card, test_mask_text_ssn,
        test_mask_text_jwt, test_mask_text_empty,
        test_mask_dict, test_mask_dict_nested,
        test_mask_json, test_mask_json_invalid,
        test_context_level_analytics, test_context_level_debugging,
        test_encryption_roundtrip, test_encryption_different_keys,
        test_key_rotation,
        test_password_hash_and_verify, test_password_verify_wrong,
        test_password_custom_iterations, test_password_custom_salt,
        test_masking_order,
    ]
    for t in tests:
        t()
    print("\n  Security: {} passed, {} failed, {} total".format(_passed, _failed, _passed + _failed))
    return _failed == 0


if __name__ == "__main__":
    run_all()