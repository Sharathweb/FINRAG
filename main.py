import uvicorn

if __name__ == "__main__":
    # This points to the 'app' object inside 'app/finrag_server.py'
    uvicorn.run("app.finrag_server:app", host="0.0.0.0", port=8000, reload=False)