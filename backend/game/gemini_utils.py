# game/gemini_utils.py
import os
import json
from google import genai
from google.genai import types
from ninja import Schema
from typing import List
from pydantic import ValidationError

class QuestionSchema(Schema):
    question: str
    options: List[str]
    answer: str
    explanation: str


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_question(level: int) -> dict:
    difficulty_map = {
        1: "easy, beginner finance question, multiple choice, simple math",
        2: "medium difficulty, some calculations, basic financial concepts",
        3: "harder, involves reasoning and multi-step finance problems",
        4: "advanced, challenging finance problem suitable for children who mastered levels 1-3"
    }
    system_instruction = (
            "You are a friendly financial literacy teacher for kids. "
            "Your tone is encouraging and simple. Always output valid JSON using this schema:"
            "{'question': str, 'options': [str], 'answer': str, 'explanation': str}"
        )
    prompt = (
    f"Generate one multiple-choice finance question for level {level} ({difficulty_map[level]}) for children."
    )    

    try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json"
                )
            )
            
            # Parse JSON
            data = json.loads(response.text)
            
            # 2. Validate against the Schema immediately!
            # This ensures if Gemini hallucinates a wrong field, we catch it here.
            return QuestionSchema(**data)

    except (json.JSONDecodeError, ValidationError) as e:
        # Fallback or retry logic could go here
        print(f"Error parsing Gemini response: {e}")
        # Return a default error question or re-raise
        raise ValueError("Failed to generate a valid question.")