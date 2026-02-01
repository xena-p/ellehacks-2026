# game/gemini_utils.py
import os
import json
import random
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


def get_gemini_client():
    """Returns the client only when called, preventing startup hangs."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in your environment variables.")
    
    return genai.Client(api_key=api_key)

def generate_question(level: int) -> dict:
    fallback_questions = {
        1: [
            {"question": "What is a 'Need'?", "options": ["A new toy", "A video game", "Healthy food", "A fancy hat"], "answer": "Healthy food", "explanation": "Needs are things you must have to live!"},
            {"question": "What does it mean to 'Save'?", "options": ["Spending all money", "Keeping money for later", "Giving money away"], "answer": "Keeping money for later"},
            {"question": "What is an 'Allowance'?", "options": ["Money for chores", "A vegetable", "A library book"], "answer": "Money for chores"}
        ],
        2: [
            {"question": "What is a 'Budget'?", "options": ["A plan for spending", "A secret password", "A math test"], "answer": "A plan for spending"},
            {"question": "What is 'Interest'?", "options": ["Extra money you earn", "A hobby", "A bank fee"], "answer": "Extra money you earn"},
            {"question": "What is a 'Debit Card'?", "options": ["A card for your own money", "A credit card", "A magic trick"], "answer": "A card for your own money"}
        ],
        3: [
            {"question": "What is compound interest?", "options": ["Interest on principal only", "Interest on principal and accumulated interest", "A flat fee"], "answer": "Interest on principal and accumulated interest"},
            {"question": "What is a stock?", "options": ["A loan to a company", "Partial ownership of a company", "Insurance"], "answer": "Partial ownership of a company"},
            {"question": "Why do prices change?", "options": ["Supply and demand", "The weather", "Random luck"], "answer": "Supply and demand"}
        ]
    }
    
    client = get_gemini_client()
    difficulty_map = {
        1: "easy, beginner finance question, multiple choice, simple math for 5 year olds",
        2: "medium difficulty, some calculations, basic financial concepts, 7 year olds",
        3: "harder, involves reasoning and multi-step finance problems, suitable for 9 year olds",
        4: "advanced, challenging finance problem suitable for children who mastered levels 1-3, suiltable for 11 year olds",
        5: "expert kid-friendly finance problem, multi-step reasoning, real-world scenario, suitable for 12 year olds"
    }
    system_instruction = (
            "You are a friendly financial literacy teacher for kids. "
            "Your tone is encouraging and simple. Always output valid JSON using this schema:"
            "{'question': str, 'options': [str], 'answer': str, 'explanation': str}"
        )
    # Use a safe lookup for difficulty description to avoid KeyError for unexpected levels
    difficulty_desc = difficulty_map.get(level, difficulty_map.get(3))

    prompt = (
        f"Generate one multiple-choice finance question for level {level} ({difficulty_desc}) for children. "
        "Make sure it's appropriate for KIDS age 3-7 and keep the question under 130 characters."
    )

    try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", #gemini-3-flash-preview, gemini-flash-latest
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

    except Exception as e:
        # Fallback or retry logic could go here
        print(f"!!! FALLBACK ACTIVATED: {e}")
        # Provide fallback pools for higher levels if missing
        fallback_questions.setdefault(4, [
            {"question": "Why is saving money helpful?", "options": ["To buy things later", "To lose it", "To throw away"], "answer": "To buy things later", "explanation": "Saving lets you afford things in the future."},
            {"question": "What does 'interest' do to your savings?", "options": ["Makes it grow", "Makes it vanish", "Keeps it the same"], "answer": "Makes it grow", "explanation": "Interest adds extra money to savings over time."}
        ])
        fallback_questions.setdefault(5, [
            {"question": "If you split $20 among 4 friends, how much each?", "options": ["$4", "$5", "$6"], "answer": "$5", "explanation": "20 divided by 4 equals 5."},
            {"question": "What is a 'budget' used for?", "options": ["Plan money use", "Hide money", "Lose money"], "answer": "Plan money use", "explanation": "Budgets help plan how to spend and save money."}
        ])

        level_pool = fallback_questions.get(level, fallback_questions[1])
        fallback_data = random.choice(level_pool)
        # Return a default error question or re-raise
        return QuestionSchema(**fallback_data)