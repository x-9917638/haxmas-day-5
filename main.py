from os import environ

from src.app import app

if __name__ == "__main__":
    port: str | None = environ.get("PORT")
    if port:
        app.run(host="127.0.0.1", port=int(port))
    else:
        print("\n[WARN]: PORT not defined, defaulting to 3000\n")
        app.run(host="127.0.0.1", port=3000)
