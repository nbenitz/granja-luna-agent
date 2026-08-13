import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.src.cli.media_vision_benchmark import _parse_json_content, run_benchmark


class _FakeResponse:
    def __init__(self, body: dict):
        self._body = json.dumps(body).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self._body


class MediaVisionBenchmarkTests(unittest.TestCase):
    def test_parse_json_content_reports_invalid_output(self):
        parsed, error = _parse_json_content("not-json")

        self.assertIsNone(parsed)
        self.assertIsNotNone(error)

    def test_run_benchmark_persists_structured_metrics(self):
        response = {
            "message": {"content": '{"descripcion_literal":"pollitos"}'},
            "total_duration": 1_000_000_000,
            "eval_count": 12,
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            image = Path(temp_dir) / "sample.jpg"
            image.write_bytes(b"fake-image")
            with (
                patch(
                    "runtime.src.cli.media_vision_benchmark.urllib.request.urlopen",
                    return_value=_FakeResponse(response),
                ),
                patch(
                    "runtime.src.cli.media_vision_benchmark._gpu_memory_mib",
                    return_value=321,
                ),
            ):
                result = run_benchmark(
                    images=[image],
                    prompt_type="photo",
                    model="test-model",
                    endpoint="http://localhost:11434",
                    timeout=1,
                )

        self.assertTrue(result["valid_json"])
        self.assertEqual(result["analysis"]["descripcion_literal"], "pollitos")
        self.assertEqual(result["gpu_memory_mib"]["before"], 321)
        self.assertEqual(result["gpu_memory_mib"]["peak_observed"], 321)
        self.assertEqual(result["ollama_metrics"]["eval_count"], 12)


if __name__ == "__main__":
    unittest.main()
