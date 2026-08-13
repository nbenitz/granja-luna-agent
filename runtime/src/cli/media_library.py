#!/usr/bin/env python3
"""Inventory the private Granja Luna media library without modifying originals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


REPO_DIR = Path(__file__).resolve().parents[3]
RUNTIME_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = Path(__file__).resolve().parents[1]
DEFAULT_ROOT = REPO_DIR / "media" / "inbox"
DEFAULT_DATABASE = RUNTIME_DIR / "state" / "media-library" / "library.sqlite3"

sys.path.insert(0, str(SRC_DIR))

from core.media_library import (  # noqa: E402
    connect_media_library,
    list_media_clusters,
    scan_media_library,
    summarize_media_library,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Granja Luna private media library")
    parser.add_argument(
        "--database", type=Path, default=DEFAULT_DATABASE, help="Ruta de la base SQLite local"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Actualiza el inventario sin modificar originales")
    scan.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Carpeta privada a inventariar")
    scan.add_argument("--burst-seconds", type=int, default=15, help="Intervalo maximo de una rafaga")
    scan.add_argument("--format", choices=("summary", "json"), default="summary")

    summary = subparsers.add_parser("summary", help="Resume el ultimo inventario persistido")
    summary.add_argument("--format", choices=("summary", "json"), default="summary")

    clusters = subparsers.add_parser("clusters", help="Lista grupos detectados")
    clusters.add_argument(
        "--type", choices=("temporal_burst", "exact_duplicate"), dest="cluster_type"
    )
    clusters.add_argument("--limit", type=int, default=20)
    clusters.add_argument("--format", choices=("summary", "json"), default="summary")

    args = parser.parse_args()
    try:
        if args.command == "scan":
            result = scan_media_library(
                args.root, args.database, burst_seconds=args.burst_seconds
            )
            print_result(result, args.format)
            return 0
        if args.command == "summary":
            with connect_media_library(args.database) as connection:
                print_result(summarize_media_library(connection), args.format)
            return 0
        if args.command == "clusters":
            with connect_media_library(args.database) as connection:
                result = list_media_clusters(
                    connection, cluster_type=args.cluster_type, limit=args.limit
                )
            if args.format == "json":
                print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            else:
                print_cluster_summary(result)
            return 0
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    parser.error("Comando no soportado")
    return 2


def print_result(result: dict[str, object], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return
    print(f"Recursos: {result.get('total', 0)}")
    print(f"Fotos: {result.get('images', 0)}")
    print(f"Videos: {result.get('videos', 0)}")
    print(f"Bytes: {result.get('bytes', 0)}")
    print(f"Con GPS: {result.get('gps_assets', 0)}")
    print(f"Errores: {result.get('errors', 0)}")
    print(f"Faltantes desde el ultimo escaneo: {result.get('missing', 0)}")
    clusters = result.get("clusters", {})
    members = result.get("cluster_members", {})
    if isinstance(clusters, dict) and isinstance(members, dict):
        for cluster_type, count in sorted(clusters.items()):
            print(f"{cluster_type}: {count} grupos / {members.get(cluster_type, 0)} recursos")
    if result.get("database"):
        print(f"Base local: {result['database']}")


def print_cluster_summary(clusters: list[dict[str, object]]) -> None:
    if not clusters:
        print("No hay grupos con ese filtro.")
        return
    for cluster in clusters:
        print(f"{cluster['id']} | {cluster['cluster_type']} | {cluster['item_count']} recursos")
        for member in cluster.get("members", []):
            if isinstance(member, dict):
                print(f"  - {member.get('captured_local_at') or 'sin fecha'} | {member['relative_path']}")


if __name__ == "__main__":
    raise SystemExit(main())
