import uvicorn
from config import configs
from app import app

if __name__ == '__main__':
    uvicorn.run(
        app,
        host='localhost',
        port=9000
    )


