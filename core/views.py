from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from django.conf import settings
import fitz  # PyMuPDF
import json
import logging
import traceback

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ===================== PAGES =====================
def home(request):
    return render(request, "core/home.html")

def test_prep(request):
    return render(request, "core/test_prep.html")

def judge(request):
    return render(request, "core/judge.html")

def grader(request):
    return render(request, "core/grader.html")

# ===================== PDF UPLOAD & INITIAL AI GRADING =====================
@csrf_exempt
def upload_pdf(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        pdf_file = request.FILES.get("file")
        if not pdf_file:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        # Read PDF text
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        if not text.strip():
            return JsonResponse({"error": "PDF is empty or could not be read."}, status=400)

        # Prepare AI grading prompt
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI DECA grader. Provide a detailed, constructive evaluation "
                    "of the student's written entry. Include a final section titled "
                    "'Actionable Suggestions / What to fix'. Be polite, professional, and clear."
                )
            },
            {"role": "user", "content": text}
        ]

        # Send to OpenAI
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages
        )
        feedback = response.choices[0].message.content.strip()
        return JsonResponse({"feedback": feedback})

    except Exception as e:
        error_msg = f"Failed to process PDF: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return JsonResponse({"error": error_msg}, status=500)


# ===================== INTERACTIVE ROLEPLAY CHAT =====================
@csrf_exempt
def roleplay_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        conversation_history = data.get("history", [])
        cluster = data.get("cluster", "Business Administration Core")
        judge_name = data.get("judge", "Judge")
        evaluate = data.get("evaluate", False)
        message = data.get("message", "")

        if evaluate:
            # Evaluation after conversation ends
            evaluation_prompt = (
                "You are a professional DECA Judge. Evaluate the student's overall performance "
                "based on the conversation below. Grade their communication, reasoning, and DECA knowledge. "
                "Provide constructive feedback in clear bullet points.\n\n"
            )
            for msg in conversation_history:
                role = "Student" if msg["role"] == "user" else "Judge"
                evaluation_prompt += f"{role}: {msg['content']}\n"

            messages = [
                {"role": "system", "content": "You are an experienced DECA competition judge."},
                {"role": "user", "content": evaluation_prompt},
            ]

        elif "Generate DECA role play prompt" in message:
            # Initial DECA prompt generation
            prompt = f"""
You are a DECA Role Play prompt generator.
Generate a realistic DECA role play scenario for the cluster "{cluster}".
Include these formatted sections:
**EVENT TITLE**
**PARTICIPANT INSTRUCTIONS**
**21ST CENTURY SKILLS**
**PERFORMANCE INDICATORS**
**EVENT SITUATION**

Address the student as if you are the judge "{judge_name}". Keep official DECA formatting.
            """
            messages = [
                {"role": "system", "content": "You are a professional DECA prompt writer."},
                {"role": "user", "content": prompt},
            ]

        else:
            # Standard conversation: respond to user
            system_msg = f"""
You are DECA Judge {judge_name} evaluating a student in the {cluster} cluster.
Always respond in this format:
1. Start with your name as the speaker.
2. Respond directly to what the student said.
3. Politely give advice or suggestions for improvement in 1-2 sentences.
Maintain a professional, constructive, and encouraging tone.
Wait until the student has submitted their full input before responding.
"""
            messages = [{"role": "system", "content": system_msg}]
            for msg in conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages
        )
        reply = response.choices[0].message.content.strip()
        return JsonResponse({"reply": reply})

    except Exception as e:
        error_msg = f"Failed to process chat: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return JsonResponse({"error": error_msg}, status=500)


# ===================== AI GRADER CHAT (Interactive follow-up) =====================
@csrf_exempt
def chat_with_grader(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get("message", "")
        history = data.get("history", [])

        system_msg = (
            "You are an AI DECA grader. Wait for the student to submit their full message before replying. "
            "Provide constructive, detailed feedback in a polite and professional tone. "
            "Always include a final 'Actionable Suggestions / What to fix' section."
        )

        messages = [{"role": "system", "content": system_msg}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages
        )
        ai_reply = response.choices[0].message.content.strip()
        return JsonResponse({"reply": ai_reply})

    except Exception as e:
        error_msg = f"Failed to continue chat: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return JsonResponse({"error": error_msg}, status=500)
