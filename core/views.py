from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from django.conf import settings
import json
import fitz  # PyMuPDF

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

        # Build GPT prompt for roleplay
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


# === PDF AI Grader ===

def extract_text_from_pdf(file):
    """Extract all text from uploaded PDF"""
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

@csrf_exempt
def upload_pdf(request):
    """
    Upload PDF, extract text, and grade it with GPT-5 based on rubric.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        pdf_file = request.FILES.get('file')
        rubric = request.POST.get("rubric", "Use standard DECA grading rubric.")

        if not pdf_file:
            return JsonResponse({"error": "No PDF file uploaded."}, status=400)

        # Extract text from PDF
        pdf_text = extract_text_from_pdf(pdf_file)

        # GPT prompt for grading
        prompt = f"""
You are a DECA written entry judge.
Grade the following written entry using this rubric:
{rubric}

Written Entry:
{pdf_text}

Provide:
- Section scores
- Detailed feedback per criterion
- Total score out of 100
Respond in clear, structured format.
"""

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are an expert DECA judge."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4
        )

        feedback = response.choices[0].message.content.strip()
        return JsonResponse({"feedback": feedback})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
