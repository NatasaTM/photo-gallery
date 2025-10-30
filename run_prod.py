# run_prod.py
import os, sys, traceback

LOG_FILE = os.path.join(
    os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__),
    "FotoGalerija_error.log",
)


def log_exception(exctype, value, tb):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n--- Uncaught exception ---\n")
        traceback.print_exception(exctype, value, tb, file=f)


sys.excepthook = log_exception
from waitress import serve
from gallery_app import create_app

if __name__ == "__main__":
    app = create_app()
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    print(f"Serving on http://{host}:{port}")
    serve(app, host=host, port=port)
