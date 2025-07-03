import logging
import azure.functions as func
import json
import os
from openai import OpenAI

# Init OpenAI client (nieuw in v1.x)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY") or "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")  # <-- vervang indien nodig tijdelijk hardcoded

def load_presets():
    return {
        "email": {
            "title": "Klantmail",
            "intro": "Hieronder vind je een conceptmail voor de klant:",
            "tone": "Energiek, professioneel en direct",
            "template": "Schrijf een energieke en professionele mail in de stijl van Ivar’s over: {input}"
        },
        "linkedin": {
            "title": "LinkedIn post",
            "intro": "Hier is een voorstel voor een LinkedIn-post:",
            "tone": "Informeel, krachtig en inspirerend",
            "template": "Schrijf een inspirerende LinkedIn-post in de stijl van Ivar’s over: {input}"
        },
        "offerte": {
            "title": "Offerte-intro",
            "intro": "Dit is een voorstel voor de inleiding van je offerte:",
            "tone": "Zakelijk, overtuigend en menselijk",
            "template": "Schrijf een zakelijke maar mensgerichte offerte-intro in de stijl van Ivar’s over: {input}"
        }
    }

def generate_output(preset_data, user_input):
    prompt = preset_data.get("template", "").replace("{input}", user_input)
    tone = preset_data.get("tone", "")

    system_message = (
        "Je bent een professionele AI-copywriter die schrijft namens Ivar’s. "
        "Gebruik altijd een energieke, heldere en no-nonsense stijl (B1-niveau), "
        "met korte actieve zinnen. Geen clichés. Geen uitleg. "
        "Alleen de tekst die direct bruikbaar is in de gekozen context."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{prompt} (Toon: {tone})"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error("⚠️ Fout bij OpenAI-call:")
        logging.error(str(e))
        return f"⚠️ AI-fout: {str(e)}"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("✅ Ivar’s Assistent API aangeroepen")

    try:
        req_body = req.get_json()
        preset = req_body.get("preset", "").lower()
        user_input = req_body.get("input", "")

        logging.info(f"🎛️ Geselecteerde preset: {preset}")
        logging.info(f"✍️ Gebruikersinput: {user_input}")

        presets = load_presets()
        if preset not in presets:
            logging.warning(f"⚠️ Preset '{preset}' niet gevonden")
            return func.HttpResponse(
                json.dumps({"error": f"Preset '{preset}' niet gevonden."}),
                mimetype="application/json",
                status_code=400
            )

        output = generate_output(presets[preset], user_input)

        return func.HttpResponse(
            json.dumps({"message": output}),
            mimetype="application/json"
        )

    except Exception as e:
        logging.error("💥 Fout in backend:")
        logging.error(str(e))
        return func.HttpResponse(
            json.dumps({"error": f"Serverfout: {str(e)}"}),
            mimetype="application/json",
            status_code=500
        )
