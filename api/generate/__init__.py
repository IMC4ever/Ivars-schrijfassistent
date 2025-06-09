import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Ivar’s Assistent API aangeroepen')
    return func.HttpResponse(
        json.dumps({"message": "Hello from Ivar’s Assistent backend!"}),
        mimetype="application/json"
    )
