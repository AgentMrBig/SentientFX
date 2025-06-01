import base64
import json
import openai
from bridge.config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

EXPECTED_KEYS = {
    "decision", "confidence", "reason",
    "TPLV1", "TPLV2", "SLLV", "critSupport", "critResistance"
}

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode("utf-8")

def request_trade_decision(context: dict, image_path: str):
    try:
        image_b64 = encode_image_to_base64(image_path)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert forex trading assistant. Based on the chart image and market context, "
                    "respond ONLY with a JSON object using the format below. Do not include any explanation outside the JSON.\n\n"
                    "{\n"
                    "  \"decision\": \"BUY | SELL | WAIT | UNSURE\",\n"
                    "  \"TPLV1\": \"target price 1\",\n"
                    "  \"TPLV2\": \"target price 2\",\n"
                    "  \"SLLV\": \"stop loss price\",\n"
                    "  \"critSupport\": \"important support level\",\n"
                    "  \"critResistance\": \"important resistance level\",\n"
                    "  \"confidence\": \"LOW | MEDIUM | HIGH\",\n"
                    "  \"reason\": \"Short explanation\"\n"
                    "}"
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Here is the current USDJPY 1-minute chart. "
                            f"Market context: {json.dumps(context)}"
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    }
                ]
            }
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )

        raw_text = response.choices[0].message.content.strip()

        # Extract JSON only (in case GPT returns extra text)
        json_start = raw_text.find("{")
        json_end = raw_text.rfind("}") + 1
        json_str = raw_text[json_start:json_end]
        decision = json.loads(json_str)

        if not EXPECTED_KEYS.issubset(decision.keys()):
            print("[Vision] Missing expected keys in response.")
            return None

        return decision

    except Exception as e:
        print(f"[Vision] Error during OpenAI Vision request: {e}")
        return None
