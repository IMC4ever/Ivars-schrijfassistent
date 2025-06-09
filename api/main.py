# main.py
from fastapi import FastAPI
app = FastAPI()

@app.get('/')
def read_root():
    return {'message': 'Hello from Ivar’s Assistent backend!'}
