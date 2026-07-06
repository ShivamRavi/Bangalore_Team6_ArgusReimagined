import sys, os
repo_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(repo_root)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
