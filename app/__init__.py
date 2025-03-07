from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import APP_DIR
from app.config.database import USER_NAME, USER_PW, DATABASE_NAME
from app.metadata import tags_metadata
from app.schemas import KUMapBaseResponse

# SQLAlchemy config
SQLALCHEMY_DATABASE_URL = f'mysql://{USER_NAME}:{USER_PW}@localhost:3306/{DATABASE_NAME}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI config
app = FastAPI(
    title='KUMap REST API',
    version='0.0.1',
    openapi_tags=tags_metadata,
)

origins = [
    'http://localhost',
    'http://localhost:3000',
    'http://localhost:3001',
    'http://127.0.0.1:51203'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 허용할 도메인 목록
    allow_credentials=True, # 쿠키 포함 여부
    allow_methods=['*'],    # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=['*'],    # 모든 HTTP 헤더 허용
)

app.mount('/static', StaticFiles(directory=os.path.join(APP_DIR, 'static')), name='static')

@app.get('/', response_model=KUMapBaseResponse)
def server_status():
    return {
        'status':'success', 
        'message':'서버가 정상적으로 동작하고 있습니다.',
    }


# include routers
from app.routes.auth import auth_router
from app.routes.geo import geo_router
from app.routes.land import land_router
from app.routes.user import user_router
from app.routes.map import map_router

app.include_router(auth_router)
app.include_router(geo_router)
app.include_router(land_router)
app.include_router(user_router)
app.include_router(map_router)
