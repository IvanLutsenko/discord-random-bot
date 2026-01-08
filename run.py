import os
import threading
import uvicorn

from web import app
from bot import start_bot  # см. ниже

def start_web():
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=start_web, daemon=True).start()
    start_bot()
