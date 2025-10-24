from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from django.conf import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def home(request):
    return render(request, "core/home.html")

def test_prep(request):
    return render(request, "core/test_prep.html")

def judge(request):
    return render(request, "core/judge.html")

@csrf_exempt
def roleplay_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        user_input = data.get("message", "").strip()
        conversation_history = data.get("history", [])

        # Build messages for GPT
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a DECA event simulator designed to generate authentic high school-level "
                    "DECA Role Play scenarios that follow official DECA event formats. Respond as a judge "
                    "interacting with the student in a role play. Ask questions, provide guidance, "
                    "and simulate a realistic competitive scenario."
                ),
            }
        ] + conversation_history + [{"role": "user", "content": user_input}]

        # Call GPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )

        ai_message = response.choices[0].message.content

        return JsonResponse({"reply": ai_message})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
