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
# FALLBACK QUESTIONS
    fallback_questions = [
        {"question": "What is compound interest?", "options": ["Interest on principal only", "Interest on principal and accumulated interest", "A flat fee"], "answer": "Interest on principal and accumulated interest"},
        {"question": "What is a stock?", "options": ["A loan to a company", "Partial ownership of a company", "A type of insurance"], "answer": "Partial ownership of a company"},
        {"question": "What is a 'Need'?", "options": ["A new toy", "A video game", "Healthy food", "A fancy hat"], "answer": "Healthy food", "explanation": "Needs are things you must have to live and stay healthy!"},
        {"question": "What does it mean to 'Save'?", "options": ["Spending all your money", "Keeping money for later", "Giving money away", "Losing your wallet"], "answer": "Keeping money for later", "explanation": "Saving is like putting money in a time machine for your future self!"},
        {"question": "What is an 'Allowance'?", "options": ["Money for chores", "A type of vegetable", "The cost of a movie", "A library book"], "answer": "Money for chores", "explanation": "An allowance is money you earn for helping out at home!"},
        {"question": "What is a 'Budget'?", "options": ["A plan for spending", "A secret password", "A type of luggage", "A math test"], "answer": "A plan for spending", "explanation": "A budget helps you make sure you have enough money for what you need!"},
        {"question": "What is 'Interest'?", "options": ["Extra money you earn", "A hobby you like", "A bank's phone number", "A tax on toys"], "answer": "Extra money you earn", "explanation": "Interest is like a 'thank you' payment from the bank for keeping your money there!"},
        {"question": "What is a 'Debit Card'?", "options": ["A card for your own money", "A credit card", "A library card", "A magic trick"], "answer": "A card for your own money", "explanation": "A debit card takes money directly from your own bank account!"},
        {"question": "What is 'Donating'?", "options": ["Giving to help others", "Buying something new", "Selling your toys", "Finding a penny"], "answer": "Giving to help others", "explanation": "Donating is sharing what you have with people or causes that need help!"},
        {"question": "What is an 'Investment'?", "options": ["Money that can grow", "A type of shoe", "A video game level", "A debt"], "answer": "Money that can grow", "explanation": "An investment is putting money into something hoping it will grow into more money later!"},
        {"question": "What is 'Income'?", "options": ["Money you earn", "Money you spend", "A type of house", "A bank fee"], "answer": "Money you earn", "explanation": "Income is the money that comes in from working or chores!"},
        {"question": "Why do prices change?", "options": ["Supply and demand", "The weather", "Magic", "Random luck"], "answer": "Supply and demand", "explanation": "If many people want something but there isn't much of it, the price usually goes up!"}
    ]    
    
    client = get_gemini_client()
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
    f"Generate one multiple-choice finance question for level {level} ({difficulty_map[level]}) for children. Make sure its appropiate for KIDS age 7-12"
    )    

    try:
            response = client.models.generate_content(
                model="gemini-1.5-flash-lite-001",
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
        fallback_data = random.choice(fallback_questions)
        # Return a default error question or re-raise
        return QuestionSchema(**fallback_data)