import uvicorn
import os
import sys

# Add backend directory to sys.path
backend_path = os.path.join(os.path.dirname(__file__), "backend")
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

if __name__ == "__main__":
    print("Starting Citizen Rights & Government Scheme Navigator server...")
    print("Web UI available at: http://localhost:8000")
    print("API Docs available at: http://localhost:8000/docs")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False, app_dir=backend_path)
