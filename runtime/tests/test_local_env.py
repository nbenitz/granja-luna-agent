import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.src.core.local_env import get_local_secret


class LocalEnvTests(unittest.TestCase):
    def test_environment_has_priority(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("GEMINI_API_KEY=file-value\n", encoding="utf-8")
            with patch.dict(os.environ, {"GEMINI_API_KEY": "process-value"}):
                value = get_local_secret("GEMINI_API_KEY", env_file)

        self.assertEqual(value, "process-value")

    def test_loads_quoted_value_without_exposing_it(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text('GEMINI_API_KEY="secret-value"\n', encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                value = get_local_secret("GEMINI_API_KEY", env_file)

        self.assertEqual(value, "secret-value")

    def test_rejects_missing_value(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("GEMINI_API_KEY=\n", encoding="utf-8")
            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaises(RuntimeError):
                    get_local_secret("GEMINI_API_KEY", env_file)


if __name__ == "__main__":
    unittest.main()
