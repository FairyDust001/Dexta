from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI
from django.conf import settings  # import settings
from django.views.decorators.csrf import csrf_exempt
import tempfile

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def home(request):
    return render(request, "core/home.html")

def test_prep(request):
    return render(request, "core/test_prep.html")

def judge(request):
    return render(request, "core/judge.html")

def digital_judge(request):
    return render(request, "core/digital_judge.html")

@csrf_exempt
def evaluate_presentation(request):
    if request.method == "POST":
        file = request.FILES.get("file")
        if not file:
            return JsonResponse({"error": "No file uploaded"}, status=400)

        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            # Send to OpenAI for evaluation
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional DECA judge evaluating student presentations."},
                    {"role": "user", "content": f"Analyze this uploaded presentation ({file.name}) and provide a detailed score (1–100) and feedback."}
                ],
            )
            result = response.choices[0].message.content
        except Exception as e:
            result = f"Error during evaluation: {str(e)}"

        return JsonResponse({"result": result})

    return JsonResponse({"error": "Invalid request method"}, status=405)

# Create your views here.
