from uvicorn import run

from ._entry import entry


def start(host: str = "0.0.0.0", port: int = 2000):
    run(app=entry, host=host, port=port)
