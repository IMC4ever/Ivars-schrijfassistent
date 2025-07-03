import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Ivar's Assistent API aangeroepen")

    try:
        data = req.get_json()
        preset = data.get("preset")
        input_text = data.get("input")
        logging.info(f"Gekregen preset: {preset}, input: {input_text}")
    except Exception as e:
        return func.HttpResponse(f"Fout in JSON: {str(e)}", status_code=400)

    return func.HttpResponse(
        json.dumps({"output": f"[{preset}] - {input_text}"}),
        mimetype="application/json"
    )
