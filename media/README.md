# Biblioteca local de medios

Las fotos y videos reales no se versionan en Git. Este directorio funciona como bandeja local para
curar material de Granja Luna sin mezclar originales, seleccionados y publicaciones.

Crear localmente:

```text
media/
├── inbox/       # Copias de fotos y videos candidatos, antiguos o nuevos
├── selected/    # Material aprobado para preparar contenido
└── published/   # Copias finales y referencia de la publicación
```

## Regla de conservación

- Conservar los archivos originales fuera de este repositorio como respaldo.
- Copiar, no mover, el material hacia `inbox/`.
- No incluir credenciales, conversaciones, datos de clientes ni documentos personales.
- Revisar ubicación GPS y otros metadatos antes de publicar.
- Registrar procedencia, fecha aproximada, animales y contexto cuando sea posible.

## Nombre recomendado

`AAAA-MM-DD_tema_descripcion_origen.ext`

Ejemplo:

`2026-07-17_brahma_pollitos_corral_telefono-nestor.jpg`

## Inventario local

Desde la raiz del repositorio:

```bash
python3 runtime/src/cli/media_library.py scan
python3 runtime/src/cli/media_library.py summary
python3 runtime/src/cli/media_library.py clusters --type temporal_burst --limit 10
```

El inventario se guarda en `runtime/state/media-library.sqlite3`. No copia binarios ni extrae
coordenadas GPS: solo registra si el bloque GPS esta presente para bloquear derivados inseguros.
Volver a ejecutar el escaneo no modifica los medios y reutiliza metadatos cuando el archivo no
cambio.
