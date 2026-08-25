# greenhouse-api

The backend half of a two-repository scenario used to exercise the orchestration
platform. Fictional client, fictional greenhouse, real FastAPI.

It exists to answer one question: when this service gains an endpoint and a new
response shape, does the ticket in `greenhouse-web` — a different repository,
whose agent never sees this code — get told the shape and write a client that
matches it?

`src/api.py` declares its own router, which is what lets the deriver resolve each
route's prefix. `src/models.py` holds the contracts; the ones an endpoint
references are published to the project scope, and that is the only path by which
the web repository can learn about them.

```
pip install -r requirements.txt
python -m pytest -q
```
