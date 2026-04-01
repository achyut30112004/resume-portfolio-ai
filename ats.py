# ats.py
import os
import json
import google.generativeai as genai

# Configure Gemini using environment variable
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL = "models/gemini-2.5-flash"


def improve_resume(resume_text: str) -> str:
    """
    Takes raw resume text and returns improved resume content in JSON format.
    """

    model = genai.GenerativeModel(MODEL)

    prompt = f"""
You are an ATS-optimization expert and resume coach.

TASK:
1. Improve clarity and grammar
2. Add relevant software engineering keywords
3. Rewrite bullet points in strong action-verb format
4. Keep it concise and ATS-friendly

Return STRICT JSON in this format only:
{{
  "summary": "Improved professional summary",
  "bullets": [
    "Improved bullet 1",
    "Improved bullet 2",
    "Improved bullet 3"
  ]
}}

RESUME:
{resume_text}
"""

    response = model.generate_content(prompt)
    return response.text
