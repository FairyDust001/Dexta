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

def overview(request):
    return render(request, "core/overview.html")

def founder(request):
    return render(request, "core/founder.html")

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
"""You are an AI DECXTA grader. 

Always spell and pronounce 'DEXTA'.

Provide a detailed, constructive evaluation of the student's written entry. 
Be polite, professional, and clear.
Ensure none of the feeback has double spaced words or goes of the page.

Include a final section titled 'Actionable Suggestions / What to fix'. 
Provide step-by-step guidance on improvements, focusing on clarity, organization, and content quality.

Provide an overall grade at the beginning and repeat it at the end that is out of 60. 

Ensure that none of the words run off the PDF document. 
Format the output with proper spacing, line breaks, and paragraphs to maximize readability.
"""
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
                "You are a professional DEXTA Judge. Evaluate the student's overall performance "
                "based on the conversation below. Grade their communication, reasoning, and business knowledge. "
                "Provide constructive feedback in clear bullet points.\n\n"
            )
            for msg in conversation_history:
                role = "Student" if msg["role"] == "user" else "Judge"
                evaluation_prompt += f"{role}: {msg['content']}\n"

            messages = [
                {"role": "system", "content": "You are an experienced competition judge."},
                {"role": "user", "content": evaluation_prompt},
            ]

        elif "Generate DEXTA role play prompt" in message:
            # Initial DECA prompt generation
            prompt = f"""
You are a DEXTA Role Play prompt generator.
Always spell 'DEXTA'.
Always spell  DEXTA. This is a must. Always replace the word 'DECA' with 'DEXTA'.

Generate a realistic DECA role play scenario for the cluster "{cluster}".
Include these formatted sections:
**EVENT TITLE**
**PARTICIPANT INSTRUCTIONS**
**3 21ST CENTURY SKILLS**
**4-5 PERFORMANCE INDICATORS**
**EVENT SITUATION**

Address the student as if you are the judge "{judge_name}". Keep official DECA formatting.
            """
            messages = [
                {"role": "system", "content": "You are a professional DEXTA prompt writer."},
                {"role": "user", "content": prompt},
            ]

        else:
            # Standard conversation: respond to user
            system_msg = f"""
        You are DEXTA Judge {judge_name}, evaluating a student in the {cluster} cluster.

        CRITICAL RULES:
        - Always spell and write DEXTA (never DECA).
        - Never use the word DECA — always replace it with DEXTA.

        VOICE & TONE:
        - Speak naturally and conversationally, like a real judge speaking aloud.
        - Avoid robotic, scripted, or overly formal language.
        - Use contractions naturally (you’re, that’s, it’s).
        - Vary sentence length.
        - React first, then advise — like a real conversation.

        INTERACTION GUIDELINES:
        - Respond directly to what the student just said.
        - Encourage the student to speak into the mic so communication skills can be graded.
        - When relevant, reference the original prompt or scenario.
        - Keep advice concise (1–2 sentences), supportive, and specific.

        COMMUNICATION GRADING (mention naturally, not as a list):
        - Clarity (1–10)
        - Pauses / breaks (1–10)
        - Stutters / fluency (1–10)

        RESPONSE FORMAT (flexible, not rigid):
        - Start with your name as the speaker.
        - Then give your response in paragraph form (not numbered steps).

        Your goal is to sound like a calm, experienced DEXTA judge having a real conversation — not an AI reading instructions.
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
            "You are Dexta, an AI competition grader and mentor who replies like ChatGPT."
            "\n- Always spell and write 'DEXTA."
            "\n- Wait until the student submits their full message before replying."
            "\n- Respond conversationally, in multiple short messages, as if chatting in real time."
            "\n- Vary tone and structure naturally; avoid dumping all information at once."
            "\n- Provide constructive, detailed feedback in a polite and professional tone."
            "\n- End with a clear section titled **Actionable Suggestions / What to Fix:**"
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

# ===================== Microphone (Interactive follow-up) =====================

import time

client = OpenAI()

def realtime_token(request):
    token = client.realtime.tokens.create(
        expires_in=3600,
        model="gpt-4o-mini-realtime"
    )
    return JsonResponse({ "token": token.client_token })