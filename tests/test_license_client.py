import hashlib
import unittest
from unittest.mock import Mock, patch

import license_client
from license_client import LicenseError


class LicenseClientTests(unittest.TestCase):
    def test_device_identifier_is_hashed_before_use(self):
        with patch.object(license_client, "_machine_identifier", return_value="raw-device-id"):
            result = license_client.get_device_id()

        expected = hashlib.sha256(
            b"lightning-ai-device-v1:raw-device-id"
        ).hexdigest()
        self.assertEqual(result, expected)
        self.assertNotEqual(result, "raw-device-id")

    def test_missing_secure_credential_backend_fails_closed(self):
        with patch.object(license_client.keyring, "get_keyring") as get_keyring:
            get_keyring.return_value.priority = 0
            with self.assertRaises(LicenseError):
                license_client.get_access_token("a" * 64)

    def test_checkout_sends_hashed_device_id_and_billing_email(self):
        response = Mock(status_code=201)
        response.json.return_value = {"checkout_url": "https://checkout.dodopayments.com/session"}
        with patch.object(license_client.requests, "request", return_value=response) as request:
            status, data = license_client.create_device_checkout(
                "b" * 64,
                " customer@example.com ",
                "trial",
            )

        self.assertEqual(status, 201)
        self.assertEqual(data["checkout_url"], "https://checkout.dodopayments.com/session")
        self.assertEqual(request.call_args.kwargs["json"], {
            "device_id": "b" * 64,
            "email": "customer@example.com",
            "mode": "trial",
        })

    def test_invalid_device_id_is_rejected_before_network_request(self):
        with patch.object(license_client.requests, "request") as request:
            with self.assertRaises(LicenseError):
                license_client.create_device_checkout("not-a-device-id", "a@example.com", "trial")
        request.assert_not_called()


if __name__ == "__main__":
    unittest.main()
