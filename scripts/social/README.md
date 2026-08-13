# Experimentos de producción social

Estos archivos preservan ediciones y automatizaciones puntuales usadas durante la etapa de
aprendizaje. No constituyen una integración de producción con Meta.

- Los scripts de Reel dependen de originales y subtítulos locales ignorados por Git.
- `share_reel_to_story_once.sh` documenta una prueba histórica, usa una ruta de esta máquina y
  ejecuta Codex con acceso amplio sobre una sesión Chrome ya autenticada.
- `share_reel_to_story_2026-08-11.sh` es otra ejecución única y fechada, autorizada para compartir
  exclusivamente el Reel 04 de las cuatro Brahma. Su flujo web produjo una tarjeta estática
  clasificada por Meta como `Foto · 6 segundos`; queda como evidencia del incidente y no debe
  reutilizarse para distribuir reels.
- No programar ni reutilizar ese script sin una autorización nueva, revisión de sus límites y una
  sesión supervisada.
- Para obtener un fragmento nativo reproducible, usar `Compartir > Tu historia` desde Facebook
  Android y confirmar después `Video` y la duración en Meta Business Suite.
- La automatización estable deberá usar la API oficial de Meta, autenticación, idempotencia y
  auditoría; no control de navegador como mecanismo permanente.

Los resultados operativos y aprendizajes correspondientes viven en `brand/reports/` y
`brand/social-media-operating-model.md`.
