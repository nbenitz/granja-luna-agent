"""Benchmark Gemini over sanitized local images or one complete video."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from runtime.src.cli.media_vision_benchmark import BRAND_CONTEXT, BURST_PROMPT, PHOTO_PROMPT
from runtime.src.core.local_env import get_local_secret


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ENV_FILE = REPO_ROOT / ".env"
API_ROOT = "https://generativelanguage.googleapis.com"

VIDEO_PROMPT = """
Analiza el video completo, incluyendo imagen y audio si existe. Distingue hechos visibles, calidad
tecnica y posibles usos editoriales. No confirmes raza, edad, sexo, salud, bienestar, ubicacion,
disponibilidad comercial ni contexto que el video no demuestre. Usa marcas de tiempo aproximadas.
Responde exclusivamente con JSON valido:
{
  "resumen_literal": "...",
  "sujetos_visibles": ["..."],
  "linea_de_tiempo": [
    {"marca_de_tiempo": "MM:SS", "hecho_visible_o_audible": "..."}
  ],
  "calidad": {
    "puntaje_1_a_5": 1,
    "estabilidad": "...",
    "nitidez": "...",
    "iluminacion": "...",
    "audio": "...",
    "problemas": ["..."]
  },
  "uso_editorial": {
    "recomendacion": "publicable_con_retoque",
    "formatos": ["reel", "historia"],
    "temas": ["..."],
    "mejores_momentos": [
      {"inicio": "MM:SS", "fin": "MM:SS", "motivo": "..."}
    ],
    "portada_sugerida": "MM:SS"
  },
  "riesgos": {
    "personas_o_menores": false,
    "datos_sensibles": false,
    "bienestar_para_revisar": false,
    "detalles": ["..."]
  },
  "afirmaciones_que_requieren_verificacion": ["..."],
  "limitaciones": ["..."],
  "confianza_0_a_1": 0.0
}
""".strip()

STRING_ARRAY = {"type": "array", "items": {"type": "string"}}
PHOTO_SCHEMA = {
    "type": "object",
    "properties": {
        "descripcion_literal": {"type": "string"},
        "sujetos_visibles": STRING_ARRAY,
        "calidad": {
            "type": "object",
            "properties": {
                "puntaje_1_a_5": {"type": "number", "minimum": 1, "maximum": 5},
                "nitidez": {"type": "string"},
                "iluminacion": {"type": "string"},
                "encuadre": {"type": "string"},
                "problemas": STRING_ARRAY,
            },
            "required": ["puntaje_1_a_5", "nitidez", "iluminacion", "encuadre", "problemas"],
            "additionalProperties": False,
        },
        "uso_editorial": {
            "type": "object",
            "properties": {
                "recomendacion": {
                    "type": "string",
                    "enum": ["publicable", "publicable_con_retoque", "solo_archivo", "descartar"],
                },
                "formatos": STRING_ARRAY,
                "ideas": STRING_ARRAY,
                "retoques_permitidos": STRING_ARRAY,
            },
            "required": ["recomendacion", "formatos", "ideas", "retoques_permitidos"],
            "additionalProperties": False,
        },
        "riesgos": {
            "type": "object",
            "properties": {
                "personas_o_menores": {"type": "boolean"},
                "datos_sensibles": {"type": "boolean"},
                "bienestar_para_revisar": {"type": "boolean"},
                "detalles": STRING_ARRAY,
            },
            "required": [
                "personas_o_menores",
                "datos_sensibles",
                "bienestar_para_revisar",
                "detalles",
            ],
            "additionalProperties": False,
        },
        "afirmaciones_que_requieren_verificacion": STRING_ARRAY,
        "confianza_0_a_1": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": [
        "descripcion_literal",
        "sujetos_visibles",
        "calidad",
        "uso_editorial",
        "riesgos",
        "afirmaciones_que_requieren_verificacion",
        "confianza_0_a_1",
    ],
    "additionalProperties": False,
}
BURST_SCHEMA = {
    "type": "object",
    "properties": {
        "resumen_de_la_escena": {"type": "string"},
        "mejor_archivo": {"type": "string"},
        "sin_candidata_adecuada": {"type": "boolean"},
        "etiquetas_sugeridas": {
            "type": "object",
            "properties": {
                "tipos_de_toma": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "panoramica_paisaje", "escena_general", "grupo_aves",
                            "retrato_detalle", "accion_proceso",
                        ],
                    },
                },
                "temas": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "pollitos", "gallinas_caseras", "gallos", "brahma",
                            "rhode_island_red", "plymouth_rock_barred", "black_star",
                            "pastoreo", "comportamiento_natural", "alimentacion", "cuidado",
                            "sanidad_con_contexto", "limpieza_e_infraestructura",
                            "incubacion_y_cria", "naturaleza_y_paisaje", "trabajo_diario",
                        ],
                    },
                },
                "pilares": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "animales_y_personalidad", "crianza_responsable",
                            "vida_libre_y_naturaleza", "trabajo_y_profesionalismo",
                            "aprendizaje_y_educacion", "razas_genetica_y_produccion",
                            "productos_y_disponibilidad", "comunidad_y_humor",
                            "fe_gratitud_y_proposito",
                        ],
                    },
                },
            },
            "required": ["tipos_de_toma", "temas", "pilares"],
            "additionalProperties": False,
        },
        "favoritos_por_intencion": {
            "type": "array",
            "minItems": 0,
            "maxItems": 2,
            "items": {
                "type": "object",
                "properties": {
                    "archivo": {"type": "string"},
                    "prioridad": {"type": "string", "enum": ["principal", "secundaria"]},
                    "intencion": {
                        "type": "string",
                        "enum": [
                            "panoramica_paisaje", "escena_general", "grupo_aves",
                            "retrato_detalle", "accion_proceso",
                        ],
                    },
                    "motivo": {"type": "string"},
                },
                "required": ["archivo", "prioridad", "intencion", "motivo"],
                "additionalProperties": False,
            },
        },
        "ranking": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "archivo": {"type": "string"},
                    "puntaje_1_a_5": {"type": "number", "minimum": 1, "maximum": 5},
                    "motivo": {"type": "string"},
                    "problemas_visibles": STRING_ARRAY,
                    "usos_sugeridos": STRING_ARRAY,
                },
                "required": [
                    "archivo", "puntaje_1_a_5", "motivo", "problemas_visibles",
                    "usos_sugeridos",
                ],
                "additionalProperties": False,
            },
        },
        "diferencias_decisivas": STRING_ARRAY,
        "uso_editorial_sugerido": STRING_ARRAY,
        "riesgos": STRING_ARRAY,
        "afirmaciones_que_requieren_verificacion": STRING_ARRAY,
        "requiere_eleccion_humana": {"type": "boolean"},
        "confianza_0_a_1": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": [
        "resumen_de_la_escena",
        "mejor_archivo",
        "sin_candidata_adecuada",
        "etiquetas_sugeridas",
        "favoritos_por_intencion",
        "ranking",
        "diferencias_decisivas",
        "uso_editorial_sugerido",
        "riesgos",
        "afirmaciones_que_requieren_verificacion",
        "requiere_eleccion_humana",
        "confianza_0_a_1",
    ],
    "additionalProperties": False,
}
VIDEO_SCHEMA = {
    "type": "object",
    "properties": {
        "resumen_literal": {"type": "string"},
        "sujetos_visibles": STRING_ARRAY,
        "linea_de_tiempo": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "marca_de_tiempo": {"type": "string"},
                    "hecho_visible_o_audible": {"type": "string"},
                },
                "required": ["marca_de_tiempo", "hecho_visible_o_audible"],
                "additionalProperties": False,
            },
        },
        "calidad": {
            "type": "object",
            "properties": {
                "puntaje_1_a_5": {"type": "number", "minimum": 1, "maximum": 5},
                "estabilidad": {"type": "string"},
                "nitidez": {"type": "string"},
                "iluminacion": {"type": "string"},
                "audio": {"type": "string"},
                "problemas": STRING_ARRAY,
            },
            "required": [
                "puntaje_1_a_5",
                "estabilidad",
                "nitidez",
                "iluminacion",
                "audio",
                "problemas",
            ],
            "additionalProperties": False,
        },
        "uso_editorial": {
            "type": "object",
            "properties": {
                "recomendacion": {
                    "type": "string",
                    "enum": ["publicable", "publicable_con_retoque", "solo_archivo", "descartar"],
                },
                "formatos": STRING_ARRAY,
                "temas": STRING_ARRAY,
                "mejores_momentos": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "inicio": {"type": "string"},
                            "fin": {"type": "string"},
                            "motivo": {"type": "string"},
                        },
                        "required": ["inicio", "fin", "motivo"],
                        "additionalProperties": False,
                    },
                },
                "portada_sugerida": {"type": "string"},
            },
            "required": [
                "recomendacion",
                "formatos",
                "temas",
                "mejores_momentos",
                "portada_sugerida",
            ],
            "additionalProperties": False,
        },
        "riesgos": PHOTO_SCHEMA["properties"]["riesgos"],
        "afirmaciones_que_requieren_verificacion": STRING_ARRAY,
        "limitaciones": STRING_ARRAY,
        "confianza_0_a_1": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": [
        "resumen_literal",
        "sujetos_visibles",
        "linea_de_tiempo",
        "calidad",
        "uso_editorial",
        "riesgos",
        "afirmaciones_que_requieren_verificacion",
        "limitaciones",
        "confianza_0_a_1",
    ],
    "additionalProperties": False,
}

RETRYABLE_HTTP_STATUS = {429, 500, 502, 503, 504}
RETRY_DELAYS_SECONDS = (2.0, 5.0)
MAX_PROVIDER_RETRY_DELAY_SECONDS = 60.0


def _provider_retry_delay(detail: str) -> float | None:
    try:
        payload = json.loads(detail)
    except (json.JSONDecodeError, TypeError):
        return None
    items = payload.get("error", {}).get("details", [])
    for item in items:
        if not isinstance(item, dict) or not str(item.get("@type", "")).endswith(
            "RetryInfo"
        ):
            continue
        raw = str(item.get("retryDelay", "")).strip().lower()
        if raw.endswith("s"):
            try:
                return max(0.0, float(raw[:-1]))
            except ValueError:
                return None
    return None


class GeminiHTTPError(RuntimeError):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        self.retry_after_seconds = _provider_retry_delay(detail)
        super().__init__(f"Gemini devolvio HTTP {status_code}: {detail}")


def _request(
    request: urllib.request.Request,
    *,
    timeout: float,
) -> tuple[bytes, dict[str, str]]:
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            headers = {key.lower(): value for key, value in response.headers.items()}
            return response.read(), headers
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GeminiHTTPError(exc.code, detail) from exc


def _json_request(
    url: str,
    *,
    api_key: str,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    timeout: float,
    extra_headers: dict[str, str] | None = None,
) -> tuple[dict[str, Any], dict[str, str]]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"x-goog-api-key": api_key}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if extra_headers:
        headers.update(extra_headers)
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    body, response_headers = _request(request, timeout=timeout)
    return (json.loads(body) if body else {}), response_headers


def _extract_response(response: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    candidates = response.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"Gemini no devolvio candidatos: {json.dumps(response, ensure_ascii=False)}")
    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    if not text:
        raise RuntimeError("Gemini devolvio una respuesta sin texto")
    return text, response.get("usageMetadata", {})


def _parse_json_content(content: str) -> tuple[Any | None, str | None]:
    try:
        return json.loads(content), None
    except json.JSONDecodeError as exc:
        return None, str(exc)


def _generate(
    *,
    api_key: str,
    model: str,
    parts: list[dict[str, Any]],
    prompt: str,
    response_schema: dict[str, Any],
    timeout: float,
) -> tuple[str, dict[str, Any], int]:
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [*parts, {"text": f"{BRAND_CONTEXT}\n\n{prompt}"}],
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
            "responseJsonSchema": response_schema,
        },
    }
    for attempt in range(len(RETRY_DELAYS_SECONDS) + 1):
        try:
            response, _ = _json_request(
                f"{API_ROOT}/v1beta/models/{model}:generateContent",
                api_key=api_key,
                method="POST",
                payload=payload,
                timeout=timeout,
            )
            content, usage = _extract_response(response)
            return content, usage, attempt
        except GeminiHTTPError as exc:
            if (
                exc.status_code not in RETRYABLE_HTTP_STATUS
                or attempt >= len(RETRY_DELAYS_SECONDS)
            ):
                raise
            delay = RETRY_DELAYS_SECONDS[attempt]
            if exc.retry_after_seconds is not None:
                delay = max(delay, exc.retry_after_seconds + 1.0)
            time.sleep(min(delay, MAX_PROVIDER_RETRY_DELAY_SECONDS))
    raise RuntimeError("Gemini agotó los reintentos sin devolver una respuesta.")


def analyze_images(
    *,
    api_key: str,
    images: list[Path],
    prompt_type: str,
    candidate_names: list[str] | None,
    editorial_intent: str | None,
    model: str,
    timeout: float,
) -> dict[str, Any]:
    missing = [str(path) for path in images if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"No existen: {', '.join(missing)}")
    names = candidate_names or [path.name for path in images]
    prompt_template = PHOTO_PROMPT if prompt_type == "photo" else BURST_PROMPT
    prompt = (
        f"{prompt_template}\n\n"
        f"Candidatos en orden de lectura (izquierda a derecha, arriba abajo): {names}"
    )
    if editorial_intent:
        prompt += f"\n\nIntencion editorial confirmada por el usuario: {editorial_intent}"
    parts = []
    for path in images:
        mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
        parts.append(
            {
                "inline_data": {
                    "mime_type": mime_type,
                    "data": base64.b64encode(path.read_bytes()).decode("ascii"),
                }
            }
        )
    started = time.perf_counter()
    content, usage, retry_count = _generate(
        api_key=api_key,
        model=model,
        parts=parts,
        prompt=prompt,
        response_schema=PHOTO_SCHEMA if prompt_type == "photo" else BURST_SCHEMA,
        timeout=timeout,
    )
    elapsed = time.perf_counter() - started
    parsed, parse_error = _parse_json_content(content)
    return {
        "provider": "google-gemini",
        "model": model,
        "media_type": "images",
        "prompt_type": prompt_type,
        "images": [str(path) for path in images],
        "candidate_names": names,
        "editorial_intent": editorial_intent,
        "elapsed_seconds": round(elapsed, 3),
        "usage_metadata": usage,
        "retry_count": retry_count,
        "valid_json": parse_error is None,
        "parse_error": parse_error,
        "analysis": parsed,
        "raw_content": content,
    }


def _upload_video(
    *,
    api_key: str,
    video: Path,
    timeout: float,
) -> dict[str, Any]:
    mime_type = mimetypes.guess_type(video.name)[0] or "video/mp4"
    size = video.stat().st_size
    _, headers = _json_request(
        f"{API_ROOT}/upload/v1beta/files",
        api_key=api_key,
        method="POST",
        payload={"file": {"display_name": video.name}},
        timeout=timeout,
        extra_headers={
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(size),
            "X-Goog-Upload-Header-Content-Type": mime_type,
        },
    )
    upload_url = headers.get("x-goog-upload-url")
    if not upload_url:
        raise RuntimeError("Gemini no devolvio la URL de carga resumible")
    request = urllib.request.Request(
        upload_url,
        data=video.read_bytes(),
        headers={
            "x-goog-api-key": api_key,
            "Content-Length": str(size),
            "X-Goog-Upload-Offset": "0",
            "X-Goog-Upload-Command": "upload, finalize",
        },
        method="POST",
    )
    body, _ = _request(request, timeout=timeout)
    response = json.loads(body)
    file_info = response.get("file", response)
    if not file_info.get("name") or not file_info.get("uri"):
        raise RuntimeError(f"Respuesta de carga incompleta: {json.dumps(response)}")
    return file_info


def _wait_for_file(
    *,
    api_key: str,
    file_info: dict[str, Any],
    timeout: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    current = file_info
    while current.get("state", "").upper() not in {"ACTIVE", "FAILED"}:
        if time.monotonic() >= deadline:
            raise TimeoutError("Gemini no termino de procesar el video dentro del plazo")
        time.sleep(2)
        current, _ = _json_request(
            f"{API_ROOT}/v1beta/{file_info['name']}",
            api_key=api_key,
            timeout=timeout,
        )
    if current.get("state", "").upper() == "FAILED":
        raise RuntimeError(f"Gemini no pudo procesar el video: {json.dumps(current)}")
    return current


def _delete_remote_file(*, api_key: str, name: str, timeout: float) -> None:
    _json_request(
        f"{API_ROOT}/v1beta/{name}",
        api_key=api_key,
        method="DELETE",
        timeout=timeout,
    )


def analyze_video(
    *,
    api_key: str,
    video: Path,
    model: str,
    timeout: float,
) -> dict[str, Any]:
    if not video.is_file():
        raise FileNotFoundError(video)
    started = time.perf_counter()
    file_info = _upload_video(api_key=api_key, video=video, timeout=timeout)
    remote_deleted = False
    try:
        active_file = _wait_for_file(
            api_key=api_key,
            file_info=file_info,
            timeout=timeout,
        )
        content, usage, retry_count = _generate(
            api_key=api_key,
            model=model,
            parts=[
                {
                    "file_data": {
                        "mime_type": active_file.get("mimeType", "video/mp4"),
                        "file_uri": active_file["uri"],
                    }
                }
            ],
            prompt=VIDEO_PROMPT,
            response_schema=VIDEO_SCHEMA,
            timeout=timeout,
        )
    finally:
        try:
            _delete_remote_file(api_key=api_key, name=file_info["name"], timeout=timeout)
            remote_deleted = True
        except Exception:
            remote_deleted = False
    elapsed = time.perf_counter() - started
    parsed, parse_error = _parse_json_content(content)
    return {
        "provider": "google-gemini",
        "model": model,
        "media_type": "video",
        "video": str(video),
        "size_bytes": video.stat().st_size,
        "elapsed_seconds": round(elapsed, 3),
        "usage_metadata": usage,
        "retry_count": retry_count,
        "remote_file_deleted": remote_deleted,
        "valid_json": parse_error is None,
        "parse_error": parse_error,
        "analysis": parsed,
        "raw_content": content,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    media = parser.add_mutually_exclusive_group(required=True)
    media.add_argument("--image", action="append", type=Path)
    media.add_argument("--video", type=Path)
    parser.add_argument("--prompt-type", choices=("photo", "burst"), default="photo")
    parser.add_argument("--candidate-name", action="append")
    parser.add_argument("--editorial-intent")
    parser.add_argument("--model", default="gemini-3.5-flash")
    parser.add_argument("--env-file", type=Path, default=DEFAULT_ENV_FILE)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    api_key = get_local_secret("GEMINI_API_KEY", args.env_file)
    if args.video:
        result = analyze_video(
            api_key=api_key,
            video=args.video,
            model=args.model,
            timeout=args.timeout,
        )
    else:
        result = analyze_images(
            api_key=api_key,
            images=args.image,
            prompt_type=args.prompt_type,
            candidate_names=args.candidate_name,
            editorial_intent=args.editorial_intent,
            model=args.model,
            timeout=args.timeout,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
