import unittest
from unittest.mock import patch

from app.crawler.llm_service import LLMService


class LlmServiceTests(unittest.TestCase):
    def test_authorization_uses_configured_api_key(self):
        service = LLMService()
        service.api_key = "unit-test-key"
        service.active_models = ["unit-test-model"]
        captured = {}

        class Response:
            status_code = 503

        class Client:
            def __init__(self, timeout):
                self.timeout = timeout

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def post(self, url, json, headers):
                captured.update(headers)
                return Response()

        with patch("app.crawler.llm_service.httpx.Client", Client):
            result = service._call_groq_json("{}", "system")

        self.assertIsNone(result)
        self.assertEqual(captured.get("Authorization"), "Bearer unit-test-key")


if __name__ == "__main__":
    unittest.main()
