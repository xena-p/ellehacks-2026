# game/gemini_utils.py
import hashlib
import os
import json
import random
from google import genai
from google.genai import types
from ninja import Schema
from typing import List
from pydantic import ValidationError
from .models import Questions, QuestionAttempt
from .schemas import GeneratedQuestionSchema



def get_gemini_client():
    """Returns the client only when called, preventing startup hangs."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in your environment variables.")
    
    return genai.Client(api_key=api_key)

def generate_question(level: int) -> dict:
    
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
    difficulty_desc = difficulty_map.get(level, difficulty_map.get(5))

    prompt = (
        f"Generate one multiple-choice finance question for level {level} ({difficulty_desc}) for children. "
        "Make sure it's appropriate for KIDS age 3-7 and keep the question under 130 characters."
    )

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
    return GeneratedQuestionSchema(**data)

    # try:
    #         response = client.models.generate_content(
    #             model="gemini-2.5-flash", #gemini-3-flash-preview, gemini-flash-latest
    #             contents=prompt,
    #             config=types.GenerateContentConfig(
    #                 system_instruction=system_instruction,
    #                 response_mime_type="application/json"
    #             )
    #         )
            
    #         # Parse JSON
    #         data = json.loads(response.text)
            
    #         # 2. Validate against the Schema immediately!
    #         # This ensures if Gemini hallucinates a wrong field, we catch it here.
    #         return QuestionSchema(**data)

    # except Exception as e:
    #     # Fallback or retry logic could go here
    #     print(f"!!! FALLBACK ACTIVATED: {e}")
    #     # Provide fallback pools for higher levels if missing
    #     level_pool = fallback_questions.get(level)
    #     if not level_pool:
    #         level_pool = fallback_questions.get(1)
    #     fallback_data = random.choice(level_pool)
    #     # Return a default error question or re-raise
    #     return QuestionSchema(**fallback_data)


def generate_and_store(level):
    generated_question = generate_question(level)
    options = list(generated_question.options)
    if len(options) != 4:
        raise ValueError("Question must have four options")

    if len(set(options)) != 4:
        raise ValueError("Options must be unique")

    if generated_question.answer not in options:
        raise ValueError("Answer must be one of the options")

    correct_index = options.index(generated_question.answer)

    fingerprint = create_question_fingerprint(
        generated_question.question,
        options
    )

    question, created = Questions.objects.get_or_create(
        fingerprint=fingerprint,
        defaults={
            "level": level,
            "question_text": generated_question.question,
            "answer_choices": options,
            "correct_answer_index": correct_index,
            "explanation": generated_question.explanation,
            "source": "gemini",
            "active": True
        }
    )
    return question

def create_question_fingerprint(question_text, options):
    """Creates a unique fingerprint for a question based on its text and options."""
    combined = question_text + ''.join(sorted(options))
    return hashlib.sha256(combined.encode('utf-8')).hexdigest()

def assign_question(game_run):
    pending = (
        game_run.question_attempts
        .filter(answered_at__isnull=True)
        .select_related("question")
        .first()
    )

    if pending:
        return pending

    try:
        question = generate_and_store(
            game_run.map_level
        )
    except Exception:
        previously_used = (
            game_run.question_attempts
            .values_list("question_id", flat=True)
        )

        question = (
            Questions.objects
            .filter(
                level=game_run.map_level,
                active=True
            )
            .exclude(id__in=previously_used)
            .order_by("?")
            .first()
        )


        if question is None:
            raise RuntimeError(
                "No fallback questions are available"
            )

    return QuestionAttempt.objects.create(
        game_run=game_run,
        question=question
    )