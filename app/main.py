from fastapi import FastAPI

app = FastAPI(title='Logistics_portal')

@app.get('/')
def read_root():
    return {'message': 'Infrastructure is working'}
