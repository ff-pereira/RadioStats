"""
    author: ffpereira
    date: 2025-09-19
"""

import os
import re
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + GEMINI_API_KEY

def ask_gemini(artist_name: str, song_names: str, max_retries: int = 5) -> str:
    prompt = f"""
You are an assistant that provides factual information about musical artists and their songs. 
Some artists may be lesser-known or local, including Portuguese music. Not every artist is portuguese, so consider global artists as well. Think hard before answering.
You should attempt to find information from any reliable sources you know, including Wikipedia, MusicBrainz, Discogs, or other widely recognized music databases. 
If information is not available, leave the fields null.

Your task is to return a JSON object containing exactly four fields:

1. "description": A short factual description of the artist (4-6 sentences). If unknown, return null.
2. "nationality": The artist's nationality using internationally standardized two-letter country codes (ISO 3166-1 alpha-2). If unknown, return null.
3. "date_of_birth": The artist's date of birth in ISO format (YYYY-MM-DD). If unknown or band, return null.
4. "date_of_death": The artist's date of death in ISO format (YYYY-MM-DD). If it is a band or the artist is alive or unknown, return null.
5. "artist_type": Either "solo" or "band". If unknown, return null.

Do not include any other information, commentary, or formatting—only return a single valid JSON object.  

Example input:
Artist: "David Bowie"
Songs: "Space Oddity, Heroes, Let's Dance, Absolute Beginners"

Expected output:
{{
  "description": "David Bowie was an English singer, songwriter, and actor, known for his distinctive voice and eclectic musical style.",
  "nationality": "GB",
  "date_of_birth": "1947-01-08",
  "date_of_death": "2016-01-10",
  "artist_type": "solo"
}}

Now, here is the artist and songs:

Artist: "{artist_name}"
Songs: "{song_names}"
"""

    headers = {
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    for attempt in range(1, max_retries + 1):
        res = requests.post(GEMINI_API_URL, headers=headers, json=payload)

        if res.status_code == 200:
            try:
                data = res.json()
                answer_str = data['candidates'][0]['content']['parts'][0]['text']
                answer_str = re.sub(r"```json|```", "", answer_str).strip()
                return json.loads(answer_str)
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                return {"error": f"Error parsing response: {e}"}

        elif res.status_code == 503:
            wait_time = 2 ** attempt  # exponential backoff: 2s, 4s, 8s, 16s, ...
            print(f"503 Overloaded. Attempt {attempt}/{max_retries}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
        elif res.status_code == 429:
            print("429 Rate Limit Exceeded. Exiting.")
            exit()
        else:
            return {"error": f"Request Failed: {res.status_code}, {res.text}"}

    return {"error": "Max retries reached. Model still overloaded."}
