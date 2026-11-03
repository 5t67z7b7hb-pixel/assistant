import hashlib
import re
import subprocess
import sys

import keyring
import requests


BILLING_API_URL = "https://assistant-site-j753.onrender.com"
KEYRING_SERVICE = "com.lightningai.desktop.entitlement"
DEVICE_ID_PATTERN = re.compile(r"^[a-f0-9]{64}$")


class LicenseError(Exception):
    pass


def _machine_identifier():
    if sys.platform == "win32":
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
        ) as key:
            identifier, _ = winreg.QueryValueEx(key, "MachineGuid")
        if not isinstance(identifier, str) or not identifier.strip():
            raise LicenseError("Windows did not provide a device identifier.")
        return identifier.strip()

    if sys.platform == "darwin":
        try:
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                check=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (OSError, subprocess.SubprocessError) as error:
            raise LicenseError("macOS could not read this device's identifier.") from error
        match = re.search(r'"IOPlatformUUID"\s*=\s*"([^"]+)"', result.stdout)
        if not match:
            raise LicenseError("macOS did not provide a device identifier.")
        return match.group(1)

    raise LicenseError("Device trials are supported on Windows and macOS only.")


def get_device_id():
    identifier = _machine_identifier()
    value = f"lightning-ai-device-v1:{identifier}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()


def _get_credential_backend():
    try:
        backend = keyring.get_keyring()
        if getattr(backend, "priority", 0) <= 0:
            raise LicenseError("Secure OS credential storage is unavailable.")
        return backend
    except LicenseError:
        raise
    except Exception as error:
        raise LicenseError("Secure OS credential storage is unavailable.") from error


def get_access_token(device_id):
    if not DEVICE_ID_PATTERN.fullmatch(device_id):
        raise LicenseError("The device identifier is invalid.")
    _get_credential_backend()
    try:
        return keyring.get_password(KEYRING_SERVICE, device_id)
    except Exception as error:
        raise LicenseError("Could not read the app's secure access token.") from error


def store_access_token(device_id, token):
    if not DEVICE_ID_PATTERN.fullmatch(device_id):
        raise LicenseError("The device identifier is invalid.")
    if not isinstance(token, str) or len(token) < 32 or len(token) > 256:
        raise LicenseError("The server returned an invalid access token.")
    _get_credential_backend()
    try:
        keyring.set_password(KEYRING_SERVICE, device_id, token)
    except Exception as error:
        raise LicenseError("Could not store the access token securely.") from error


def clear_access_token(device_id):
    if not DEVICE_ID_PATTERN.fullmatch(device_id):
        raise LicenseError("The device identifier is invalid.")
    _get_credential_backend()
    try:
        keyring.delete_password(KEYRING_SERVICE, device_id)
    except keyring.errors.PasswordDeleteError:
        return
    except Exception as error:
        raise LicenseError("Could not clear the app's secure access token.") from error


def _request_json(method, path, *, token=None, payload=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        response = requests.request(
            method,
            f"{BILLING_API_URL}{path}",
            headers=headers,
            json=payload,
            timeout=(5, 20),
        )
    except requests.RequestException as error:
        raise LicenseError("Could not reach the billing service. Check your internet connection.") from error

    try:
        data = response.json()
    except ValueError as error:
        raise LicenseError("The billing service returned an invalid response.") from error
    if not isinstance(data, dict):
        raise LicenseError("The billing service returned an invalid response.")
    if response.status_code == 401:
        return response.status_code, data
    if response.status_code >= 400 and not (
        response.status_code == 409
        and data.get("code") == "TRIAL_ALREADY_USED"
    ):
        message = data.get("error")
        if not isinstance(message, str):
            message = "The billing service could not complete this request."
        raise LicenseError(message)
    return response.status_code, data


def check_entitlement(token):
    status, data = _request_json(
        "GET",
        "/api/entitlements",
        token=token,
    )
    return status, data


def create_device_checkout(device_id, email, mode):
    if not DEVICE_ID_PATTERN.fullmatch(device_id):
        raise LicenseError("The device identifier is invalid.")
    if mode not in {"trial", "subscription"}:
        raise LicenseError("The requested billing option is invalid.")
    if not isinstance(email, str) or not email.strip() or len(email) > 254:
        raise LicenseError("Enter the billing email used for checkout.")
    return _request_json(
        "POST",
        "/api/billing/device-checkout",
        payload={
            "device_id": device_id,
            "email": email.strip(),
            "mode": mode,
        },
    )
