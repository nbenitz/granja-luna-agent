#!/usr/bin/env python3
"""Operational inbox CLI for Granja Luna.

This CLI persists pending proposals only. It does not confirm purchases, stock,
sanitary events, or tasks as operational facts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


RUNTIME_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INBOX = RUNTIME_DIR / "state" / "inbox.jsonl"

sys.path.insert(0, str(SRC_DIR))

from core.dry_run import build_dry_run  # noqa: E402
from core.inbox import (  # noqa: E402
    STATUSES,
    append_inbox_entry,
    build_inbox_entry,
    filter_inbox_entries,
    find_inbox_entry,
    format_inbox_detail,
    format_inbox_table,
    load_inbox_entries,
    summarize_inbox,
    update_inbox_entry_status,
    write_inbox_entries,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Granja Luna operational inbox")
    parser.add_argument("--inbox", type=Path, default=DEFAULT_INBOX, help="Ruta del inbox JSONL")
    subparsers = parser.add_subparsers(dest="command", required=True)

    capture = subparsers.add_parser("capture", help="Analiza un mensaje y lo guarda como pendiente")
    capture.add_argument("message", help="Mensaje natural a analizar y guardar")
    capture.add_argument("--context", help="Contexto/memoria auxiliar opcional")
    capture.add_argument("--today", help="Fecha ISO para pruebas o reproduccion")
    capture.add_argument(
        "--format",
        choices=("summary", "json"),
        default="summary",
        dest="output_format",
        help="Formato de salida. Por defecto: summary.",
    )

    list_parser = subparsers.add_parser("list", help="Lista entradas del inbox")
    list_parser.add_argument("--status", choices=tuple(sorted(STATUSES)), help="Filtrar por estado")
    list_parser.add_argument("--limit", type=int, help="Cantidad maxima de entradas a mostrar")
    list_parser.add_argument(
        "--format",
        choices=("table", "json"),
        default="table",
        dest="output_format",
        help="Formato de salida. Por defecto: table.",
    )

    show = subparsers.add_parser("show", help="Muestra una entrada del inbox")
    show.add_argument("entry_id", help="ID de entrada")
    show.add_argument(
        "--format",
        choices=("summary", "json"),
        default="summary",
        dest="output_format",
        help="Formato de salida. Por defecto: summary.",
    )

    review = subparsers.add_parser("review", help="Marca una entrada revisada sin aplicar cambios reales")
    review.add_argument("entry_id", help="ID de entrada")
    review.add_argument("--status", required=True, choices=tuple(sorted(STATUSES)), help="Nuevo estado")
    review.add_argument("--notes", help="Notas de revision")
    review.add_argument(
        "--format",
        choices=("summary", "json"),
        default="summary",
        dest="output_format",
        help="Formato de salida. Por defecto: summary.",
    )

    summary = subparsers.add_parser("summary", help="Resume el inbox")
    summary.add_argument(
        "--format",
        choices=("summary", "json"),
        default="summary",
        dest="output_format",
        help="Formato de salida. Por defecto: summary.",
    )

    args = parser.parse_args()

    if args.command == "capture":
        return capture_entry(args)
    if args.command == "list":
        return list_entries(args)
    if args.command == "show":
        return show_entry(args)
    if args.command == "review":
        return review_entry(args)
    if args.command == "summary":
        return print_summary(args)
    parser.error("Comando no soportado")
    return 2


def capture_entry(args: argparse.Namespace) -> int:
    dry_run = build_dry_run(args.message, today=args.today, context=args.context)
    entry = build_inbox_entry(dry_run)
    append_inbox_entry(args.inbox, entry)
    if args.output_format == "json":
        print(json.dumps(entry, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_inbox_detail(entry))
        print(f"\nGuardado en: {args.inbox}")
    return 0


def list_entries(args: argparse.Namespace) -> int:
    entries = filter_inbox_entries(load_inbox_entries(args.inbox), status=args.status)
    if args.limit is not None:
        entries = entries[-max(args.limit, 0) :]
    if args.output_format == "json":
        print(json.dumps(entries, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_inbox_table(entries))
    return 0


def show_entry(args: argparse.Namespace) -> int:
    try:
        entry = find_inbox_entry(load_inbox_entries(args.inbox), args.entry_id)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if args.output_format == "json":
        print(json.dumps(entry, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_inbox_detail(entry))
    return 0


def review_entry(args: argparse.Namespace) -> int:
    entries = load_inbox_entries(args.inbox)
    try:
        entry = update_inbox_entry_status(entries, args.entry_id, args.status, notes=args.notes)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    write_inbox_entries(args.inbox, entries)
    if args.output_format == "json":
        print(json.dumps(entry, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_inbox_detail(entry))
        print("")
        print("Nota: revision guardada. No se aplicaron cambios operativos.")
    return 0


def print_summary(args: argparse.Namespace) -> int:
    summary = summarize_inbox(load_inbox_entries(args.inbox))
    if args.output_format == "json":
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("Granja Luna inbox summary")
        print("")
        print(f"Total: {summary['total']}")
        print(f"Requieren confirmacion: {summary['requires_confirmation']}")
        print(f"Por estado: {summary['by_status']}")
        print(f"Por riesgo: {summary['by_risk']}")
        print(f"Por dominio: {summary['by_primary_domain']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
