import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.src.cli.media_gemini_benchmark import (
    BURST_SCHEMA,
    GeminiHTTPError,
    _extract_response,
    _generate,
    _provider_retry_delay,
    analyze_images,
)
from runtime.src.cli.media_vision_benchmark import BRAND_CONTEXT, BURST_PROMPT


class MediaGeminiBenchmarkTests(unittest.TestCase):
    def test_burst_schema_allows_no_candidate_or_up_to_two_favorites(self):
        favorites = BURST_SCHEMA["properties"]["favoritos_por_intencion"]

        self.assertEqual(favorites["minItems"], 0)
        self.assertEqual(favorites["maxItems"], 2)
        self.assertEqual(
            favorites["items"]["properties"]["prioridad"]["enum"],
            ["principal", "secundaria"],
        )
        self.assertIn("afirmaciones_que_requieren_verificacion", BURST_SCHEMA["required"])

    def test_prompts_keep_visual_claims_unconfirmed(self):
        self.assertIn("foto tampoco demuestra", BRAND_CONTEXT)
        self.assertIn("intenciones distintas", BURST_PROMPT)
        self.assertIn("consejos sanitarios", BURST_PROMPT)
        self.assertIn("no permite evaluar ni determinar pureza", BRAND_CONTEXT)

    def test_extract_response_returns_text_and_usage(self):
        text, usage = _extract_response(
            {
                "candidates": [{"content": {"parts": [{"text": '{"ok":true}'}]}}],
                "usageMetadata": {"totalTokenCount": 12},
            }
        )

        self.assertEqual(text, '{"ok":true}')
        self.assertEqual(usage["totalTokenCount"], 12)

    def test_analyze_images_records_structured_result(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            image = Path(temp_dir) / "sample.jpg"
            image.write_bytes(b"fake-image")
            with patch(
                "runtime.src.cli.media_gemini_benchmark._generate",
                return_value=(
                    '{"descripcion_literal":"pollitos"}',
                    {"totalTokenCount": 10},
                    1,
                ),
            ):
                result = analyze_images(
                    api_key="test-key",
                    images=[image],
                    prompt_type="photo",
                    candidate_names=None,
                    editorial_intent="detalle",
                    model="test-model",
                    timeout=1,
                )

        self.assertTrue(result["valid_json"])
        self.assertEqual(result["analysis"]["descripcion_literal"], "pollitos")
        self.assertEqual(result["editorial_intent"], "detalle")
        self.assertEqual(result["usage_metadata"]["totalTokenCount"], 10)
        self.assertEqual(result["retry_count"], 1)

    def test_generate_retries_transient_provider_errors(self):
        response = {
            "candidates": [{"content": {"parts": [{"text": '{"ok":true}'}]}}],
            "usageMetadata": {"totalTokenCount": 12},
        }
        with (
            patch(
                "runtime.src.cli.media_gemini_benchmark._json_request",
                side_effect=[GeminiHTTPError(503, "busy"), (response, {})],
            ) as request,
            patch("runtime.src.cli.media_gemini_benchmark.time.sleep") as sleep,
        ):
            content, usage, retry_count = _generate(
                api_key="test-key",
                model="test-model",
                parts=[],
                prompt="test",
                response_schema={"type": "object"},
                timeout=1,
            )

        self.assertEqual(content, '{"ok":true}')
        self.assertEqual(usage["totalTokenCount"], 12)
        self.assertEqual(retry_count, 1)
        self.assertEqual(request.call_count, 2)
        sleep.assert_called_once_with(2.0)

    def test_generate_honors_provider_retry_info(self):
        detail = (
            '{"error":{"details":[{"@type":"type.googleapis.com/google.rpc.RetryInfo",'
            '"retryDelay":"32s"}]}}'
        )
        response = {
            "candidates": [{"content": {"parts": [{"text": '{"ok":true}'}]}}],
            "usageMetadata": {},
        }
        self.assertEqual(_provider_retry_delay(detail), 32.0)
        with (
            patch(
                "runtime.src.cli.media_gemini_benchmark._json_request",
                side_effect=[GeminiHTTPError(429, detail), (response, {})],
            ),
            patch("runtime.src.cli.media_gemini_benchmark.time.sleep") as sleep,
        ):
            _, _, retry_count = _generate(
                api_key="test-key",
                model="test-model",
                parts=[],
                prompt="test",
                response_schema={"type": "object"},
                timeout=1,
            )

        self.assertEqual(retry_count, 1)
        sleep.assert_called_once_with(33.0)


if __name__ == "__main__":
    unittest.main()
