"""Run a small, local Ollama vision benchmark over selected media derivatives."""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


BRAND_CONTEXT = """
Estas analizando evidencia visual real de Granja Luna, una granja avicola familiar de seis
hectareas. El objetivo es seleccionar material autentico para Facebook e Instagram, documentar el
proyecto y educar a amantes de las aves. No inventes raza, edad, sexo, salud, cantidad, ubicacion,
fecha, disponibilidad comercial ni condiciones no visibles. No diagnostiques bienestar o salud:
solo senala indicios visuales que requieran revision humana. Marca cualquier persona, menor,
documento, matricula, telefono, coordenada, acceso o dato sensible. La publicacion siempre requiere
aprobacion humana. Una foto tampoco demuestra por si sola que un transporte, alojamiento,
calefaccion, alimentacion, tratamiento o practica sean seguros, adecuados o reglamentarios. No
conviertas expresiones de marca como vida libre, crianza responsable, felices o resistentes en
hechos visualmente probados. Conserva de forma explicita cualquier incertidumbre indicada por el
usuario, especialmente sobre raza pura, salud, edad o manejo. Una foto puede documentar rasgos
visibles para una evaluacion posterior, pero no permite evaluar ni determinar pureza racial o
calidad genetica. No llames manejo sanitario, bioseguridad o crianza responsable a una escena solo
por su apariencia. Si el usuario identifica un proceso historico concreto —por ejemplo, el paso de
incubadora a criadero— conserva ese significado y no lo reemplaces por otro proceso generico.
""".strip()


PHOTO_PROMPT = """
Evalua esta imagen como candidato de contenido. `recomendacion` debe ser uno de: `publicable`,
`publicable_con_retoque`, `solo_archivo` o `descartar`. Cada elemento de `formatos` debe ser uno de:
`feed`, `historia`, `reel_portada`, `educativo` o `catalogo`. Responde exclusivamente con JSON
valido:
{
  "descripcion_literal": "solo lo claramente visible",
  "sujetos_visibles": ["..."],
  "calidad": {
    "puntaje_1_a_5": 1,
    "nitidez": "...",
    "iluminacion": "...",
    "encuadre": "...",
    "problemas": ["..."]
  },
  "uso_editorial": {
    "recomendacion": "publicable_con_retoque",
    "formatos": ["feed", "educativo"],
    "ideas": ["..."],
    "retoques_permitidos": ["recorte, luz o limpieza que no altere el hecho"]
  },
  "riesgos": {
    "personas_o_menores": false,
    "datos_sensibles": false,
    "bienestar_para_revisar": false,
    "detalles": ["..."]
  },
  "afirmaciones_que_requieren_verificacion": ["..."],
  "confianza_0_a_1": 0.0
}
""".strip()


BURST_PROMPT = """
Las tomas pertenecen a una misma rafaga. Pueden llegar como imagenes separadas o como una sola
lamina de paneles numerados; en ambos casos siguen el orden de lectura y los nombres incluidos al
final del mensaje. Debes incluir todos los candidatos una sola vez. El contexto humano sobre la
escena y la granja tiene prioridad; tu tarea es aportar lectura visual, calidad, encuadre,
obstrucciones, diferencias y posibles usos. No supongas que todo material debe servir para el
lanzamiento de Facebook. Elige una favorita principal alineada con el contexto y, solo si aporta un
angulo o uso realmente distinto, una secundaria. Puedes indicar que no existe una candidata
adecuada. Compara solo diferencias visibles y sugiere etiquetas sin presentarlas como hechos
confirmados. Si dos fotos optimizan intenciones distintas —por ejemplo, paisaje e historia frente a
detalle y protagonismo— explica el intercambio y conserva una secundaria en vez de forzar un unico
ganador universal. Separa los problemas visibles de las afirmaciones que necesitan datos externos;
no propongas consejos sanitarios, de temperatura, alimentacion o bienestar basados solo en las
imagenes. Responde exclusivamente con JSON valido:
{
  "resumen_de_la_escena": "...",
  "mejor_archivo": "nombre exacto o cadena vacia si ninguna sirve",
  "sin_candidata_adecuada": false,
  "etiquetas_sugeridas": {
    "tipos_de_toma": ["escena_general"],
    "temas": ["pollitos"],
    "pilares": ["crianza_responsable"]
  },
  "favoritos_por_intencion": [
    {
      "archivo": "nombre exacto",
      "prioridad": "principal",
      "intencion": "escena_general",
      "motivo": "..."
    }
  ],
  "ranking": [
    {
      "archivo": "nombre exacto",
      "puntaje_1_a_5": 1,
      "motivo": "...",
      "problemas_visibles": ["..."],
      "usos_sugeridos": ["feed, historia, reel, carrusel, educativo, comercial o archivo"]
    }
  ],
  "diferencias_decisivas": ["nitidez, encuadre, gesto, obstrucciones o luz"],
  "uso_editorial_sugerido": ["..."],
  "riesgos": ["..."],
  "afirmaciones_que_requieren_verificacion": ["..."],
  "requiere_eleccion_humana": true,
  "confianza_0_a_1": 0.0
}
""".strip()


VIDEO_FRAMES_PROMPT = """
Estas imagenes son fotogramas extraidos de videos distintos; no describas movimiento, sonido ni el
video completo como si los hubieras observado. Evalua cada fotograma como muestra preliminar y
portada posible. Responde exclusivamente con JSON valido:
{
  "fotogramas": [
    {
      "archivo": "nombre exacto",
      "descripcion_literal": "...",
      "calidad_1_a_5": 1,
      "sirve_como_portada": false,
      "posible_tema": "...",
      "problemas_o_riesgos": ["..."]
    }
  ],
  "limitaciones": ["un fotograma no representa necesariamente el video completo"],
  "confianza_0_a_1": 0.0
}
""".strip()


PROMPTS = {
    "photo": PHOTO_PROMPT,
    "burst": BURST_PROMPT,
    "video-frames": VIDEO_FRAMES_PROMPT,
}


def _gpu_memory_mib() -> int | None:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return max(int(value.strip()) for value in result.stdout.splitlines() if value.strip())
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError):
        return None


def _monitor_gpu(stop: threading.Event, samples: list[int]) -> None:
    while not stop.wait(0.5):
        value = _gpu_memory_mib()
        if value is not None:
            samples.append(value)


def _encode_images(paths: list[Path]) -> list[str]:
    return [base64.b64encode(path.read_bytes()).decode("ascii") for path in paths]


def _parse_json_content(content: str) -> tuple[Any | None, str | None]:
    try:
        return json.loads(content), None
    except json.JSONDecodeError as exc:
        return None, str(exc)


def run_benchmark(
    *,
    images: list[Path],
    prompt_type: str,
    model: str,
    endpoint: str,
    timeout: float,
    num_ctx: int = 4096,
    candidate_names: list[str] | None = None,
) -> dict[str, Any]:
    missing = [str(path) for path in images if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"No existen: {', '.join(missing)}")

    names = candidate_names or [path.name for path in images]
    prompt = (
        f"{BRAND_CONTEXT}\n\n{PROMPTS[prompt_type]}\n\n"
        f"Candidatos en orden de lectura (izquierda a derecha, arriba abajo): {names}"
    )
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "keep_alive": "5m",
        "options": {"temperature": 0, "num_ctx": num_ctx},
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": _encode_images(images),
            }
        ],
    }
    request = urllib.request.Request(
        f"{endpoint.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    gpu_before = _gpu_memory_mib()
    samples: list[int] = []
    stop = threading.Event()
    monitor = threading.Thread(target=_monitor_gpu, args=(stop, samples), daemon=True)
    monitor.start()
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw_response = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama devolvio HTTP {exc.code}: {detail}") from exc
    finally:
        elapsed = time.perf_counter() - started
        stop.set()
        monitor.join(timeout=2)

    ollama_response = json.loads(raw_response)
    content = ollama_response.get("message", {}).get("content", "")
    parsed, parse_error = _parse_json_content(content)
    gpu_after = _gpu_memory_mib()
    observed_gpu_values = [
        value for value in (gpu_before, *samples, gpu_after) if value is not None
    ]
    durations = {
        key: ollama_response.get(key)
        for key in (
            "total_duration",
            "load_duration",
            "prompt_eval_count",
            "prompt_eval_duration",
            "eval_count",
            "eval_duration",
        )
    }
    return {
        "model": model,
        "prompt_type": prompt_type,
        "num_ctx": num_ctx,
        "images": [str(path) for path in images],
        "candidate_names": names,
        "elapsed_seconds": round(elapsed, 3),
        "gpu_memory_mib": {
            "before": gpu_before,
            "peak_observed": max(observed_gpu_values) if observed_gpu_values else None,
            "after": gpu_after,
        },
        "ollama_metrics": durations,
        "valid_json": parse_error is None,
        "parse_error": parse_error,
        "analysis": parsed,
        "raw_content": content,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", action="append", required=True, type=Path)
    parser.add_argument("--prompt-type", choices=sorted(PROMPTS), required=True)
    parser.add_argument("--model", default="qwen3-vl:4b-instruct")
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434")
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--num-ctx", type=int, default=4096)
    parser.add_argument("--candidate-name", action="append")
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = run_benchmark(
        images=args.image,
        prompt_type=args.prompt_type,
        model=args.model,
        endpoint=args.endpoint,
        timeout=args.timeout,
        num_ctx=args.num_ctx,
        candidate_names=args.candidate_name,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
