from ninja import NinjaAPI
from .gemini_utils import generate_question, QuestionSchema
#from .models import Question
api = NinjaAPI()

@api.get("/hello")
def hello(request):
    return {"message": "Hello from your Game Backend!"}

@api.get("/math_question")
def get_math_question(request):
    return {
        "question": "5 + 3",
        "answer": 8,
        "options": [6, 8, 9, 10]
    }


@api.get("/generate-quiz/{level}", response=QuestionSchema)
def get_quiz_question(request, level: int):
    if level not in [1, 2, 3, 4]:
         # You can raise HttpError or return specific codes here
         return api.create_response(request, {"detail": "Invalid Level"}, status=400)

    try:
        # returns a validated QuestionSchema object directly
        return generate_question(level)
    except ValueError:
        return api.create_response(request, {"detail": "Generation failed"}, status=503)