# CNC control UI

Vite + React + TypeScript frontend for the Pi 5 CNC HTTP API. You build it
on a development machine. The production files land in `pi5/static/` and are
served by the same FastAPI/uvicorn process, so the Raspberry Pi never needs
Node.js, nginx, or a second web server.

## Develop (laptop)

Run the API locally first. Simulator mode is enough:

```bash
cd pi5
cp .env.example .env   # set CNC_PASSPHRASE; CNC_SIMULATOR=true
python -m cnc_api
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173/`). Vite proxies
`/health`, `/commands`, `/axis`, `/spindle`, `/emergency-stop`, `/noop`, and
`/docs` to `http://127.0.0.1:8000`. There is no hardcoded LAN IP and no
production API base URL — the UI always uses relative paths such as
`fetch("/health")`.

Enter the same passphrase as `CNC_PASSPHRASE`. It is sent as the
`X-CNC-Passphrase` header (never on the query string) and kept in
`sessionStorage` for this tab only.

## Production build

```bash
cd frontend
npm install
npm run build
```

This replaces `pi5/static/` with the new HTML/JS/CSS (`index.html` plus
`assets/`). Commit `pi5/static/` so a Pi checkout can serve the UI with zero
Node.

## On the Pi

From `pi5/`, with the venv and `.env` as in `pi5/README.md`:

```bash
python -m cnc_api
```

On a phone or laptop on the same LAN, open `http://<pi-lan-ip>:8000/`.
Unlock with the passphrase in the page — do not put it in the URL.
