import logging
import azure.functions as func
import json
import os

def load_presets():
    path = os.path.join(os.path.dirname(__file__), 'presets.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_output(preset_data, user_input):
    template = preset_data.get("template", "Schrijf iets over: {input}")
    tone = preset_data.get("tone", "")
    intro = preset_data.get("intro", "")
    
    # Hier komt straks echte AI-logica, voor nu een dummy response
    generated = template.replace("{input}", user_input)
    return f"{intro}\n\n{generated}\n\n(Toon: {tone})"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Ivar’s Assistent API aangeroepen')

    try:
        preset = req_body.get("preset", "").lower()  # <-- voegt .lower() toe
user_input = req_body.get("input")

presets = load_presets()
if preset not in presets:
    
            return func.HttpResponse(
                json.dumps({"error": f"Preset '{preset}' niet gevonden."}),
                mimetype="application/json",
                status_code=400
            )
        
        response = generate_output(presets[preset], user_input)

        return func.HttpResponse(
            json.dumps({"message": response}),
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Fout in backend: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Er ging iets mis in de backend."}),
            mimetype="application/json",
            status_code=500
        )
