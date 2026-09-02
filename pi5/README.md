# Pi 5 CNC HTTP API

FastAPI service that runs on the Raspberry Pi 5 and drives the three-axis CNC
through a Raspberry Pi Pico 2 W. HTTP requests are translated into 10-byte USB
serial command frames. The Pico firmware in `pico2_w/` is the source of truth
for the protocol; this API does not change it.

The throwaway script `main.py` is **left in place** as a low-level serial
smoke test (it talks to `COM3` from Windows). Use this FastAPI service for
normal operation.

## Setup

On the Pi 5, from this `pi5/` directory:

```bash
source activate_venv.sh
cp .env.example .env
# edit .env and set CNC_PASSPHRASE to a long random string
python -m pip install -r requirements.txt
```

The app **refuses to start** if `CNC_PASSPHRASE` is unset or empty.

`spidev` in `requirements.txt` is a leftover for Pi GPIO experiments and is
not used by this API. On Windows, `pip install -r requirements.txt` may fail
on that line; comment it out. The HTTP API only needs pyserial plus the
FastAPI stack.

### Finding the serial port

The Pico enumerates as USB CDC. On Raspberry Pi OS it is usually `/dev/ttyACM0`:

```bash
ls -l /dev/ttyACM*
# after plugging the Pico in:
dmesg | tail
```

If you have another CDC device, it may be `/dev/ttyACM1`. Set `CNC_SERIAL_PORT`
accordingly. The Windows smoke test in `main.py` uses `COM3` for the same
device.

The Pico resets when the serial port is opened. The API opens the port **once**
at process start, waits `CNC_SERIAL_OPEN_DELAY_SECONDS` (default 2s), and keeps
it open for the process lifetime.

### Simulator (no Pico)

Set `CNC_SIMULATOR=true` to replace the serial port with a fake that logs
frames and always replies `'1'`. Use this on a laptop or CI.

## Running

Working directory must be `pi5/` so the `cnc_api` package is importable. Bind
to `0.0.0.0` so other machines on the LAN can reach it:

```bash
cd pi5
source activate_venv.sh   # or: source venv/bin/activate
python -m cnc_api
```

Equivalent uvicorn invocation:

```bash
uvicorn cnc_api.app:create_app --factory --host 0.0.0.0 --port 8000
```

Listen address is `http://<pi5-lan-ip>:8000`. The control UI is `/`. Interactive
docs: `/docs`.

HTTP only — no TLS. See [Security](#security).

## Control UI

The browser UI lives in `frontend/` (Vite + React). **Build it on a laptop**,
not on the Pi. `npm run build` writes static files into `pi5/static/`, which
this API serves. The Pi only needs Python.

On a development machine:

```bash
cd frontend
npm install
npm run build
```

Commit `pi5/static/` so a Pi checkout works with no Node.js. Then run the API
as above and open `http://<pi-lan-ip>:8000/` from a phone or laptop on the LAN.

Enter the CNC passphrase in the page. It is sent as `X-CNC-Passphrase` (never
in the URL) and kept in `sessionStorage` for that browser tab until you close
the tab or tap Forget passphrase.

Local UI development (API on port 8000, Vite on 5173): see `frontend/README.md`.
Vite proxies API paths to `http://127.0.0.1:8000`; `CNC_SIMULATOR=true` is fine.

## Environment variables

Loaded from the process environment and from `pi5/.env` (via pydantic-settings).
All names are prefixed with `CNC_`.

| Variable | Default | Meaning |
|---|---|---|
| `CNC_PASSPHRASE` | *(required)* | Shared secret for machine-control endpoints |
| `CNC_SERIAL_PORT` | `/dev/ttyACM0` | USB CDC device path |
| `CNC_SERIAL_BAUD` | `115200` | Must match the Pico USB stdio baud |
| `CNC_SERIAL_OPEN_DELAY_SECONDS` | `2.0` | Wait after open for the Pico to reset |
| `CNC_MESSAGE_TIMEOUT_PER_COMMAND` | `1.0` | Seconds of read-timeout budget per character in a frame (×10 ≈ 10s per frame) |
| `CNC_MAX_COMMAND_LENGTH` | `500` | Max length of a batch command string (and of `repeat`) |
| `CNC_MAX_REPEAT` | `100` | Max `repeat` on single-command endpoints |
| `CNC_SIMULATOR` | `false` | `true` / `1` to use the fake serial backend |
| `CNC_LOCK_WAIT_SECONDS` | `60` | How long a request waits for the serial lock before `409` |

Copy `.env.example` to `.env`. `.env` is gitignored; never commit a passphrase.

## Authentication

Every machine-control endpoint requires the passphrase in a **header**, never
in the query string (query strings end up in access logs):

- `X-CNC-Passphrase: <passphrase>`
- or `Authorization: Bearer <passphrase>`

Comparison uses `secrets.compare_digest`. Missing or wrong credentials return
`401` with a JSON body:

```json
{"success": false, "error": "unauthorized", "message": "...", "frames_sent": []}
```

`GET /health` and `GET /commands` do not require auth.

## Concurrency

The Pico protocol is strictly request/response: one 10-byte frame in, one
status byte out. All serial access is serialised with a `threading.Lock`.
Endpoints are sync `def` functions so FastAPI runs them in the threadpool.

A second request **queues** until the in-flight sequence finishes, up to
`CNC_LOCK_WAIT_SECONDS`. If it still cannot obtain the lock it returns **409**
(`error: "busy"`). Raise `CNC_LOCK_WAIT_SECONDS` if you send long batches
(each step is ~0.5s on the firmware, so 10 commands ≈ 5s).

## HTTP status mapping

| Situation | HTTP | Notes |
|---|---|---|
| Pico replied `'1'` for every frame | `200` | `success: true` |
| Pico replied `'0'` for a frame | `200` | `success: false`, `failing_frame_index` set; remaining frames are **not** sent |
| Invalid protocol character | `422` | Names the character and its index; nothing is written to serial |
| Missing / wrong passphrase | `401` | |
| Serial lock wait expired | `409` | |
| Serial port not open / not connected | `503` | |
| Timed out waiting for the Pico reply | `504` | Input buffer is flushed so the next request cannot read a stale byte |
| Unexpected non-`1`/`0` reply | `200` | `success: false`; buffer flushed; no further frames |

Machine-control responses always include `success`, `frames_sent` (the exact
10-character strings written), `commands_executed` (original characters in
frames that returned `'1'`), and `message`.

## Endpoint table

Single-command routes accept an optional JSON body `{"repeat": N}` (`N` default
1). The server expands that into a command string and splits it into 10-byte
frames, padding the last frame with `n`.

| Method | Path | Protocol | Meaning |
|---|---|---|---|
| POST | `/axis/x/forward` | `X` | +1 step X (blocked by emergency stop) |
| POST | `/axis/x/backward` | `x` | −1 step X (blocked by emergency stop) |
| POST | `/axis/x/forward/forced` | `A` | +1 step X even during emergency stop |
| POST | `/axis/x/backward/forced` | `a` | −1 step X even during emergency stop |
| POST | `/axis/y/forward` | `Y` | +1 step Y (blocked by emergency stop) |
| POST | `/axis/y/backward` | `y` | −1 step Y (blocked by emergency stop) |
| POST | `/axis/y/forward/forced` | `B` | +1 step Y even during emergency stop |
| POST | `/axis/y/backward/forced` | `b` | −1 step Y even during emergency stop |
| POST | `/axis/z/forward` | `Z` | +1 step Z (blocked by emergency stop) |
| POST | `/axis/z/backward` | `z` | −1 step Z (blocked by emergency stop) |
| POST | `/axis/z/forward/forced` | `C` | +1 step Z even during emergency stop |
| POST | `/axis/z/backward/forced` | `c` | −1 step Z even during emergency stop |
| POST | `/spindle/on` | `S` | Spindle on (ignored if emergency stop is active) |
| POST | `/spindle/off` | `s` | Spindle off |
| POST | `/emergency-stop` | `E` | Latch emergency stop (spindle off; normal jogs refused until reset) |
| POST | `/emergency-stop/reset` | `R` | Clear the emergency-stop latch |
| POST | `/noop` | `n` | No-op / padding |
| POST | `/commands` | *(batch)* | Arbitrary string of the characters above |
| GET | `/health` | — | Whether the serial port is open (no auth) |
| GET | `/commands` | — | Alphabet and path catalog (no auth) |

Forced moves exist so the machine can be jogged off a tripped limit switch.

## curl examples

Replace `PASS` and the host as needed.

Health (no auth):

```bash
curl -s http://192.168.1.50:8000/health
```

One X step:

```bash
curl -s -X POST http://192.168.1.50:8000/axis/x/forward \
  -H "X-CNC-Passphrase: PASS"
```

25 X steps in one call:

```bash
curl -s -X POST http://192.168.1.50:8000/axis/x/forward \
  -H "X-CNC-Passphrase: PASS" \
  -H "Content-Type: application/json" \
  -d '{"repeat": 25}'
```

Spindle on, Bearer token:

```bash
curl -s -X POST http://192.168.1.50:8000/spindle/on \
  -H "Authorization: Bearer PASS"
```

Batch string (chunked into 10-byte frames automatically):

```bash
curl -s -X POST http://192.168.1.50:8000/commands \
  -H "X-CNC-Passphrase: PASS" \
  -H "Content-Type: application/json" \
  -d '{"commands": "XYzzxxxZZZZZ"}'
```

Trigger emergency stop:

```bash
curl -s -X POST http://192.168.1.50:8000/emergency-stop \
  -H "X-CNC-Passphrase: PASS"
```

Reset emergency stop, then a forced X jog:

```bash
curl -s -X POST http://192.168.1.50:8000/emergency-stop/reset \
  -H "X-CNC-Passphrase: PASS"

curl -s -X POST http://192.168.1.50:8000/axis/x/forward/forced \
  -H "X-CNC-Passphrase: PASS" \
  -H "Content-Type: application/json" \
  -d '{"repeat": 5}'
```

## Protocol (fixed by firmware)

- USB CDC, 115200 baud. Every message is exactly 10 ASCII bytes; shorter
  strings are right-padded with `n`. After those 10 bytes the firmware runs
  each character in order and writes back **one** byte: `'1'` if every step
  succeeded, `'0'` if any step failed or an unrecognised character was seen.
- Unrecognised characters also switch the spindle off. This API rejects them
  with 422 so they never reach the wire.
- A motor step sleeps ~500ms on the Pico (`ENA_SETTLE_TIME_MS` twice plus
  direction/pulse), so a full frame can take ~5 seconds. The read timeout is
  `10 * CNC_MESSAGE_TIMEOUT_PER_COMMAND` seconds per frame.

## Tests

From `pi5/`, with the venv active:

```bash
pytest
```

Tests use FastAPI's `TestClient` and the simulated serial backend. They cover
auth accept/reject, invalid characters, 10-byte padding, chunking of strings
longer than 10 characters, and stopping when the fake replies `'0'`.

## Security

This service is HTTP-only on a trusted home Wi-Fi network. The passphrase
travels in plaintext. There is no TLS and no payload encryption. Anyone who
can read LAN traffic or reach port 8000 and guess/steal the passphrase can
move the machine. Do not expose this port to the internet.
