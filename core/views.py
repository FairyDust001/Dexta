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
        user_input = data.get("message", "")
        conversation_history = data.get("history", [])
        cluster = data.get("cluster", "Business Administration Core")
        judge = data.get("judge", "Default Judge")

        # Build GPT prompt
        prompt = f"""
You are a DECA Role Play prompt generator.
Generate a high school DECA Role Play scenario with official DECA formatting.
Include these sections clearly with bold headings and proper spacing:

1) EVENT TITLE
2) PARTICIPANT INSTRUCTIONS
3) 21ST CENTURY SKILLS:
  - Critical Thinking – Reason effectively and use systems thinking.
  - Problem Solving – Make judgments and decisions and solve problems.
  - Communication and Collaboration – Communicate clearly and show evidence of collaboration.
  - Creativity and Innovation – Show evidence of creativity.
4) PERFORMANCE INDICATORS
5) EVENT SITUATION

Instructions:
- Use uppercase headings for each section.
- Use bullet points for instructions, skills, and performance indicators.
- Use dashes or numbering for sub-points.
- Keep spacing consistent and easy to read.
- Event Situation must start with: "You are to assume the role of..."
- Tailor the scenario for the judge "{judge}" and cluster "{cluster}".
- Respond as plain text but formatted exactly as a DECA role play paper.
        
        """

        # Call GPT-5-mini without unsupported parameters
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are an expert DECA prompt generator."},
                {"role": "user", "content": prompt}
            ]
        )

        ai_message = response.choices[0].message.content.strip()
        return JsonResponse({"reply": ai_message})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

