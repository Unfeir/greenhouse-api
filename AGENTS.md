# House rules for greenhouse-api

These are mandatory and override defaults.

## Measurements never cross the wire as floats

Every temperature figure in a response body is a **string with exactly one
decimal place** — `"18.5"`, never `18.5`. Rounding is half-up.

This is not a style preference. Binary floats do not represent one decimal place
exactly, and two services formatting the same reading disagreed in a customer
report; the argument that followed cost more than the change. Computation stays
in `Decimal`; serialisation is the string.

So a response model declares `mean_celsius: str`, not `float`. The same applies
to any future aggregate over temperature.

Humidity and counts are unaffected: humidity stays a float, counts stay `int`.

## Everything else

Routers are created in the module that uses them. Endpoints return pydantic
models rather than dicts. Tests use `fastapi.testclient` and assert on the JSON
body.
