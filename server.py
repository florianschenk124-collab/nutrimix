#!/usr/bin/env python3
"""
NutrientMixer API Server.

Lokal (Entwicklung):
    python server.py
    python server.py --reload

Produktion (Railway/Docker):
    uvicorn api.main:app --host 0.0.0.0 --port $PORT

API-Docs:
    http://localhost:8000/docs
"""

import argparse
import os
import uvicorn


def main():
    parser = argparse.ArgumentParser(description="NutrientMixer API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=None, help="Port (default: 8000 oder $PORT)")
    parser.add_argument("--reload", action="store_true", help="Auto-Reload bei Änderungen")
    args = parser.parse_args()

    port = args.port or int(os.environ.get("PORT", 8000))
    host = args.host

    print(f"═══════════════════════════════════════════")
    print(f"  NutrientMixer API Server v0.5.0-alpha")
    print(f"  http://{host}:{port}")
    print(f"  Docs: http://{host}:{port}/docs")
    print(f"═══════════════════════════════════════════")

    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
