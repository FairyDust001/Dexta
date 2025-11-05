from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI
from django.conf import settings
import fitz  # PyMuPDF
import logging
import traceback

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# ===================== PAGES =====================
def grader(request):
    return render(request, "core/grader.html")

<<<<<<< Updated upstream
# ===================== NON-STREAMING ROLEPLAY CHAT =====================
@csrf_exempt
def roleplay_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        conversation_history = data.get("history", [])
        cluster = data.get("cluster", "Business Administration Core")
        judge_name = data.get("judge", "Default Judge")
        evaluate = data.get("evaluate", False)

        if evaluate:
            # Evaluation prompt
            prompt = "Provide a detailed DECA-style evaluation of the presenter’s performance based on these responses:\n"
            for msg in conversation_history:
                role = "Student" if msg["role"] == "user" else "AI Judge"
                prompt += f"{role}: {msg['content']}\n"
        else:
            # Generate new roleplay prompt
            prompt = f"""
You are a DECA Role Play prompt generator.
Generate a high school DECA Role Play scenario with official DECA formatting.
Include these sections clearly with bold headings and proper spacing:

1) EVENT TITLE
2) PARTICIPANT INSTRUCTIONS
3) 21ST CENTURY SKILLS:
  - Critical Thinking
  - Problem Solving
  - Communication and Collaboration
  - Creativity and Innovation
4) PERFORMANCE INDICATORS
5) EVENT SITUATION

Tailor scenario for judge "{judge_name}" and cluster "{cluster}".
Respond as plain text formatted like an official DECA role play.
            """

        messages = [
            {"role": "system", "content": "You are an expert DECA prompt generator and AI judge."},
            {"role": "user", "content": prompt},
        ]

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages
        )

        reply = response.choices[0].message.content.strip()
        return JsonResponse({"reply": reply})

    except Exception as e:
        error_msg = f"Failed to generate roleplay: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return JsonResponse({"error": error_msg}, status=500)
=======
>>>>>>> Stashed changes

# ===================== PDF GRADER =====================
def extract_text_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = "".join(page.get_text() for page in doc)
        if not text.strip():
            raise ValueError("PDF contains no extractable text.")
        return text
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")

@csrf_exempt
def upload_pdf(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)
    try:
        pdf_file = request.FILES.get("file")
        if not pdf_file:
            return JsonResponse({"error": "No PDF file uploaded."}, status=400)

<<<<<<< Updated upstream
        pdf_text = extract_text_from_pdf(pdf_file)
        rubric_text = "Use standard DECA grading rubric."

        rubric_file = request.FILES.get("rubric")
        if rubric_file:
            try:
                rubric_candidate = extract_text_from_pdf(rubric_file)
                if rubric_candidate.strip():
                    rubric_text = rubric_candidate
            except ValueError:
                logger.warning("Rubric PDF extraction failed. Using default rubric.")
=======
        try:
            pdf_text = extract_text_from_pdf(pdf_file)
        except ValueError as e:
            logger.error(f"PDF extraction failed: {str(e)}\n{traceback.format_exc()}")
            return JsonResponse({"error": str(e)}, status=400)

        # Optional rubric (default)
        rubric_text = "Use standard DECA grading rubric."
>>>>>>> Stashed changes

        prompt = f"""
You are a DECA written entry judge.
Grade the following written entry using this rubric:
{rubric_text}

Written Entry:
{pdf_text}

Respond in **ChatGPT-style** format:
- Grade out of 60
- Bold section headers (I, II, III...)
- Use dashes/bullets for feedback
- Leave spacing between sections
- **Include a final 'Actionable Suggestions / What to fix' section with numbered items**
        """

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are an expert DECA judge. Format output like ChatGPT with bold headers, bullets, spacing, and actionable suggestions."},
                {"role": "user", "content": prompt},
            ],
        )

        feedback = response.choices[0].message.content.strip()
        return JsonResponse({"feedback": feedback})

    except Exception as e:
        error_msg = f"Unexpected server error: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return JsonResponse({"error": error_msg}, status=500)

<<<<<<< Updated upstream
# ===================== AI GRADER CHAT =====================
@csrf_exempt
def chat_with_grader(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        message = data.get("message", "")
        history = data.get("history", [])

        prompt = "You are an AI DECA grader. Continue the conversation with the student. Respond in **ChatGPT-style** format:\n"
        for msg in history[-6:]:
            role = "Student" if msg["role"] == "user" else "AI Grader"
            prompt += f"{role}: {msg['content']}\n"
        prompt += f"Student: {message}\nAI Grader:"

        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": "You are an expert DECA judge. Format output with bold section headers, bullets, spacing, and always include a final 'Actionable Suggestions / What to fix' section."},
                {"role": "user", "content": prompt},
            ],
        )
        ai_reply = response.choices[0].message.content.strip()
        return JsonResponse({"reply": ai_reply})

    except Exception as e:
        error_msg = f"Failed to continue chat: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        return JsonResponse({"error": error_msg}, status=500)

=======
>>>>>>> Stashed changes
