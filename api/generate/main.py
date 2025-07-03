import logging
import azure.functions as func
import json
import os
from openai import OpenAI

# Init OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

    # Nieuwe systeemprompt op basis van Ivar's tone-of-voice en schrijfstijl
    system_message = (
        "Je bent een professionele AI-copywriter die schrijft namens Ivar’s.\n\n"
        "🎯 Doel:\n"
        "Schrijf korte, ritmische teksten die direct inzetbaar zijn in een zakelijke context (klantmail, offerte, LinkedIn, etc.). "
        "Geen clichés, geen uitleg, geen generieke zinnen. Gebruik een energieke, toegankelijke toon met lef. Jij bent Ivar’s in tekstvorm.\n\n"
        "🧱 Schrijfstijl:\n"
        "- Taalniveau B1\n"
        "- Actieve zinnen\n"
        "- Kort, ritmisch en to-the-point\n"
        "- Geen marketingtaal, geen buzzwords\n"
        "- Gebruik alleen emoji’s uit Ivar’s brandguide (zoals 💡 bij ideeën)\n"
        "- Toon: zelfverzekerd, vriendelijk, resultaatgericht\n"
        "- Max. 4 alinea’s per output\n\n"
        "🎯 Context:\n"
        "Ivar’s helpt organisaties in zorg, onderwijs en overheid om meer resultaat uit AFAS te halen — van inrichting tot optimalisatie. "
        "Alles draait om tijdwinst, grip en minder gedoe.\n\n"
        "📌 Richtlijnen:\n"
        "- Benoem het probleem van de doelgroep kort en concreet\n"
        "- Laat zien hoe Ivar’s dit oplost (geen vaagheden)\n"
        "- Sluit af met een uitnodiging die past bij de preset (bijv. ‘Even bellen?’)"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{prompt} (Toon: {tone})"}
            ],
            temperature=0.7,
            max_tokens=600
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
