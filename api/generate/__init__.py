import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Ivar’s Assistent API is aangeroepen")
    try:
        req_body = req.get_json()
        user_input = req_body.get('input', '')
        preset = req_body.get('preset', 'email')

        response_text = f"Je koos preset '{preset}' en typte: '{user_input}'"
        return func.HttpResponse(
            json.dumps({"message": response_text}),
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"message": f"Fout: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )
