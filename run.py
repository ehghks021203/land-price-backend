from app import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=51203,
        # ssl_certfile="./cert/server.crt",
        # ssl_keyfile="./cert/server.key"
    )
