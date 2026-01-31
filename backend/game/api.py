from ninja import NinjaAPI

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