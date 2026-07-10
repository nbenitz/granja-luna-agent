# Web local

Estado: `mvp_local`

Aplicacion responsive para usar Granja Luna desde un celular conectado a la misma red que la computadora.

## Desarrollo

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r runtime/requirements-dev.txt
uvicorn runtime.src.web.app:app --host 0.0.0.0 --port 8000 --reload
```

Desde la computadora: `http://127.0.0.1:8000`.

Desde el celular: `http://IP_LOCAL_DE_LA_COMPUTADORA:8000`.

## QA de navegador

```bash
npm install
npx playwright install chromium
npm run test:e2e
```

Playwright usa estado temporal y verifica el flujo de una compra con multiples items en telefono y escritorio. No escribe entradas de prueba en el inbox local.

## Estado local

- `runtime/state/inbox.jsonl`
- `runtime/state/usage-events.jsonl`

Ambos archivos estan ignorados por git.

## Limite actual

La UI acepta dictado desde el teclado del celular. La captura directa del microfono requiere HTTPS y no forma parte de este corte.
