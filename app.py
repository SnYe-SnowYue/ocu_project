import sys

from ocu_app import create_app


if sys.version_info < (3, 10):
    raise RuntimeError("Python 3.10+ is required. Please recreate .venv with py -3.10 or newer.")

app = create_app()


if __name__ == "__main__":
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )
