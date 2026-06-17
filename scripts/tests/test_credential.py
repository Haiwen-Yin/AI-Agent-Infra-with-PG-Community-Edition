"""AI Agent Infra v3.6.2 - PG Community Edition - Credential & Config Tests"""

import sys
import os
import json
import tempfile
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.connection_crypto import (
    encrypt_credential_for_distribution,
    decrypt_credential_from_distribution,
    save_agent_config,
    load_agent_config,
    encrypt_section,
    decrypt_section,
    generate_admin_token as crypto_generate_admin_token,
    verify_admin_token as crypto_verify_admin_token,
    rotate_admin_token,
)
from lib.agent_api import (
    generate_admin_token,
    verify_admin_token,
)
from lib.connection import close_pool

TS = str(int(time.time()))


def test_encrypt_decrypt_credential():
    cred_data = {
        "username": "PG_TEST_USER",
        "password": "pg_test_password_123",
        "host": "10.10.10.131",
        "port": "5432",
        "dbname": "ai_agent",
    }
    token = "AT_test_distribution_token"
    encrypted = encrypt_credential_for_distribution(cred_data, token)
    assert "credential_encrypted" in encrypted
    assert "salt" in encrypted

    decrypted = decrypt_credential_from_distribution(
        encrypted["credential_encrypted"],
        encrypted["salt"],
        token,
    )
    assert decrypted["username"] == "PG_TEST_USER"
    assert decrypted["password"] == "pg_test_password_123"
    assert decrypted["host"] == "10.10.10.131"
    assert decrypted["port"] == "5432"
    assert decrypted["dbname"] == "ai_agent"
    print("PASS: test_encrypt_decrypt_credential")


def test_encrypt_with_wrong_key_fails():
    cred_data = {"username": "X", "password": "Y", "host": "Z", "port": "5432", "dbname": "db"}
    encrypted = encrypt_credential_for_distribution(cred_data, "AT_correct_token")
    try:
        decrypt_credential_from_distribution(
            encrypted["credential_encrypted"],
            encrypted["salt"],
            "AT_wrong_token",
        )
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("PASS: test_encrypt_with_wrong_key_fails")


def test_save_agent_config():
    cred_data = {
        "username": "PG_CONFIG_TEST",
        "password": "config_test_pwd",
        "host": "10.10.10.131",
        "port": "5432",
        "dbname": "ai_agent",
    }
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        config_path = f.name

    try:
        save_agent_config("config-test-agent-" + TS, cred_data, config_path)
        with open(config_path) as f:
            raw = json.load(f)
        assert "end_user" in raw
        assert "_encrypted" in raw["end_user"]
        assert "password" not in json.dumps(raw)

        loaded = load_agent_config(config_path)
        assert loaded["username"] == "PG_CONFIG_TEST"
        assert loaded["password"] == "config_test_pwd"
        assert loaded["host"] == "10.10.10.131"
        assert loaded["port"] == "5432"
        assert loaded["dbname"] == "ai_agent"
        print("PASS: test_save_agent_config")
    finally:
        os.unlink(config_path)


def test_load_agent_config():
    cred_data = {
        "username": "PG_LOAD_TEST",
        "password": "load_test_pwd",
        "host": "10.10.10.131",
        "port": "5432",
        "dbname": "ai_agent",
    }
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        config_path = f.name

    try:
        save_agent_config("load-test-agent-" + TS, cred_data, config_path)
        loaded = load_agent_config(config_path)
        assert loaded["agent_id"] == "load-test-agent-" + TS
        assert loaded["username"] == "PG_LOAD_TEST"
        print("PASS: test_load_agent_config")
    finally:
        os.unlink(config_path)


def test_load_nonexistent_config():
    try:
        load_agent_config("/tmp/pg_nonexistent_config_" + TS + ".json")
        assert False, "Should have raised FileNotFoundError"
    except (FileNotFoundError, OSError):
        pass
    print("PASS: test_load_nonexistent_config")


def test_generate_admin_token():
    token = generate_admin_token()
    assert token is not None
    assert token.startswith("AT_")
    assert len(token) > 10
    print(f"PASS: test_generate_admin_token (token={token[:16]}...)")


def test_verify_admin_token():
    token = generate_admin_token()
    assert verify_admin_token(token)
    assert not verify_admin_token("AT_invalid_token_12345")
    assert not verify_admin_token("")
    print("PASS: test_verify_admin_token")


def test_rotate_admin_token():
    old_token = generate_admin_token()
    assert verify_admin_token(old_token)

    new_token = generate_admin_token()
    assert verify_admin_token(new_token)
    assert not verify_admin_token(old_token)
    print("PASS: test_rotate_admin_token")


def test_verify_invalid_token():
    assert not verify_admin_token("")
    assert not verify_admin_token("not_a_token")
    assert not verify_admin_token("AT_")
    print("PASS: test_verify_invalid_token")


def run_all():
    passed = 0
    failed = 0
    for test_fn in [
        test_encrypt_decrypt_credential,
        test_encrypt_with_wrong_key_fails,
        test_save_agent_config,
        test_load_agent_config,
        test_load_nonexistent_config,
        test_generate_admin_token,
        test_verify_admin_token,
        test_rotate_admin_token,
        test_verify_invalid_token,
    ]:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test_fn.__name__} - {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    close_pool()
    print(f"\nCredential Tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
