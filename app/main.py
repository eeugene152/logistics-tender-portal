from fastapi import FastAPI
from app.api.v1.auth import router as router_auth
from app.api.v1.admin import router as router_admin

app = FastAPI(title='Logistics_portal')


@app.get('/')
def read_root():
    return {'message': 'Infrastructure is working'}


app.include_router(router_auth, prefix='/auth', tags=['Auth'])
app.include_router(router_admin)
