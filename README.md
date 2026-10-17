# vp-router

vp-router is a minimal FastAPI experiment by Syed Abrar Ali for managing a "virtual port" routing table: a mapping from short channel names (`A`, `B`, ...) to local TCP port numbers. It was written to test the idea of a tiny control-plane service that other local programs could query to find out which port a given channel currently lives on, instead of hard-coding ports in each of them.

## Where it is used

This is a sandbox / proof of concept rather than a deployed service. It served as the starting point for a routing layer where an existing asyncio socket server (not included here) would consult the table to forward connections. The accompanying HTML page is a bare-bones admin form for adding mappings.

## How it works

- `main.py` holds the whole service: a module-level dictionary `ROUTING_TABLE = {'A': 9001}` and two endpoints.
  - `POST /add_route` takes a JSON body validated by the Pydantic model `Route {channel: str, port: int}` and inserts or overwrites the mapping, returning a confirmation message.
  - `GET /routes` returns the current dictionary.
- The table lives in process memory only; restarting the server resets it to `{'A': 9001}`.
- `index.html` ("Virtual Port Manager") has two inputs and a button. `addRoute()` posts `{channel, port}` to `/add_route` and reloads the page. The `#routeList` div is present but nothing fills it yet.
- A comment in `main.py` notes the intended next step: run the existing asyncio server in a background thread or in FastAPI's startup event so it can read `ROUTING_TABLE` directly.

| File | Role |
|------|------|
| `main.py` | FastAPI app, in-memory routing table, `/add_route`, `/routes` |
| `index.html` | Static admin form calling `/add_route` |

## Setup

Requirements: Python 3.9+, `fastapi`, `uvicorn`, `pydantic` (installed with FastAPI).

```bash
git clone <repo-url> ~/vp
cd ~/vp
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn
```

There is no configuration file or environment variable; the seed mapping is the `ROUTING_TABLE` literal in `main.py`.

## Usage

```bash
uvicorn main:app --reload --port 8000
```

```bash
curl localhost:8000/routes
# {"A":9001}

curl -X POST localhost:8000/add_route -H 'Content-Type: application/json' \
  -d '{"channel": "B", "port": 9002}'
# {"message":"Channel B mapped to 9002"}

curl localhost:8000/routes
# {"A":9001,"B":9002}
```

`index.html` is not served by `main.py`. To use the form, serve it from the same origin as the API, for example by adding

```python
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory=".", html=True), name="static")
```

at the bottom of `main.py` and opening `http://localhost:8000/`. Opening the file directly from disk will not work because the form uses a relative `/add_route` URL.

## Project structure

```
vp/
├── main.py
└── index.html
```

## Limitations and notes

- In-memory only; no persistence, no delete endpoint, no validation of port ranges.
- No authentication; any client that can reach the port can rewrite the table.
- The HTML never lists existing routes (the `#routeList` container is empty) and simply reloads after each submit.
- `asyncio` and `threading` are imported but unused; the forwarding server they were meant for is not part of this repository.
