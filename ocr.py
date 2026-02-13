import base64
import json
from groq import Groq
import os

def get_codes_from_image_groq(image_path, groq_api_key):
    """
    Extracts map-code mappings from an image file using the Groq Vision model.
    """
    client = Groq(api_key=groq_api_key)

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    chat_completion = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct", # Using a general vision model for image analysis
        messages=[
            {
                "role": "system",
                "content": "Extract match data from this Overwatch screenshot. For each row:\n- Map name\n- Replay code (6 chars in orange badge)\n- Result: \"Win\" (green), \"Loss\" (red), or \"Draw\" (gray)\n\nReturn JSON only:\n[{\"map\": \"Ilios\", \"replay_code\": \"NC7PT1\", \"result\": \"Win\"}] Note: Overwatch maps should be one of the following options: Busan, Ilios, Lijiang Tower, Nepal, Oasis, Samoa, Antarctic Peninsula, Circuit Royal, Dorado, Havana, Junkertown, Rialto, Route 66, Shambali Monastery, Watchpoint: Gibraltar, Blizzard World, Eichenwalde, Hollywood, King's Row, Midtown, Numbani, Paraíso, Colosseo, Esperança, New Queen Street, Runasapi, Suravasa, New Junk City, Aatlis. Interpret the best option as the map."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the match data from the image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        temperature=0.0, # Set temperature to 0 for more deterministic output
        max_completion_tokens=1024,
        top_p=1,
        stop=None
    )

    response_content = chat_completion.choices[0].message.content
    try:
        # The model might return some text before or after the JSON, so we need to extract the JSON part
        json_start = response_content.find('[')
        json_end = response_content.rfind(']') + 1
        json_string = response_content[json_start:json_end]
        
        extracted_data = json.loads(json_string)
        
        return extracted_data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Groq API response: {e}")
        print(f"Groq API response: {response_content}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print(f"Groq API response: {response_content}")
        return None