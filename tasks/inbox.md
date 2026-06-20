# Inbox

Este archivo queda como vista humana/manual de tareas.

El inbox operativo inicial del runtime vive en `runtime/state/inbox.jsonl` y se gestiona con:

```bash
python3 runtime/src/cli/granja_inbox.py capture "Mensaje de la granja"
python3 runtime/src/cli/granja_inbox.py list
python3 runtime/src/cli/granja_inbox.py review inbox-id --status needs_edit --notes "Falta dato"
```

Las entradas generadas por el runtime quedan en estado `pending_review`; no son tareas activas ni hechos confirmados.

Formato sugerido:

```markdown
- [ ] YYYY-MM-DD — Tarea breve
  - Dominio:
  - Estado:
  - Riesgo:
  - Fuente:
  - Próximo paso:
```
