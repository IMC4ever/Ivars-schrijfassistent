def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Ivar’s Assistent API aangeroepen')

    try:
        req_body = req.get_json()
        preset = req_body.get("preset", "").lower()
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
