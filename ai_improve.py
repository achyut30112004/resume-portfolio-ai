# ai_improve.py
"""
AI Resume Improvement helper.

Uses OpenAI to:
- Clean and improve resume text
- Make bullets clearer and more impactful
- Add missing keywords naturally (if job description is given)

Main function:
    improve_resume(resume_data, job_description=None) -> str

In app.py we call:
    from ai_improve import improve_resume
"""

import os
import json
from openai import OpenAI


# -------- Helpers -------- #

def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY not set. Please export it or put it in your .env file."
        )
    return OpenAI(api_key=api_key)


def _normalize_resume_data(resume_json_or_dict):
    """
    Accepts either a dict or a JSON string (like we used in app.py)
    and returns a clean Python dict.
    """
    if isinstance(resume_json_or_dict, str):
        try:
            data = json.loads(resume_json_or_dict)
        except json.JSONDecodeError:
            # if it's plain text, wrap it
            data = {"raw": resume_json_or_dict}
    elif isinstance(resume_json_or_dict, dict):
        data = resume_json_or_dict
    else:
        data = {"raw": str(resume_json_or_dict)}

    return {
        "name": data.get("name", ""),
        "education": data.get("education", []),
        "experience": data.get("experience", []),
        "skills": data.get("skills", []),
        "phone": data.get("phone", ""),
        "email": data.get("email", ""),
    }


def _build_prompt(resume_data, job_description: str | None = None) -> str:
    """
    Create a detailed prompt for the model.
    """
    edu_text = "\n".join(f"- {e}" for e in resume_data["education"])
    exp_text = "\n".join(f"- {e}" for e in resume_data["experience"])
    skills_text = ", ".join(resume_data["skills"])

    jd_block = ""
    if job_description:
        jd_block = f"""
Job Description (JD) to target:

{job_description}
"""

    prompt = f"""
You are a senior technical recruiter and resume expert.

I will give you resume information extracted from a PDF.
Your tasks:

1. Rewrite this as a clean, ATS-friendly resume in English.
2. Improve clarity, grammar, and impact of bullet points.
3. Make sure the wording is strong, but still realistic for a final-year B.Tech CSE student.
4. Keep the content suitable for fresher / internship roles in software / AI / backend.
5. Use clear sections: SUMMARY, SKILLS, EDUCATION, EXPERIENCE, PROJECTS (if possible).
6. At the end, add a short section: "SUGGESTED IMPROVEMENTS" with 3–5 bullet points.

Resume data:

Name: {resume_data['name']}
Email: {resume_data['email']}
Phone: {resume_data['phone']}

Education:
{edu_text or '- (not provided)'}

Experience:
{exp_text or '- (not provided)'}

Skills:
{skills_text or '- (not provided)'}

{jd_block}

Now, return ONLY the improved resume text in Markdown (no extra explanation).
"""
    return prompt


# -------- Main function -------- #

def improve_resume(resume_json_or_dict, job_description: str | None = None) -> str:
    """
    Use OpenAI to generate an improved version of the resume.

    :param resume_json_or_dict: dict OR JSON string with fields
        {name, education, experience, skills, phone, email}
    :param job_description: optional JD text to tailor the resume
    :return: improved resume as Markdown/plain text
    """
    client = _get_client()
    resume_data = _normalize_resume_data(resume_json_or_dict)
    prompt = _build_prompt(resume_data, job_description)

    # You can change the model if needed
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are an expert in resume writing and ATS optimization."
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        temperature=0.7,
        max_tokens=900,
    )

    improved_text = response.choices[0].message.content.strip()
    return improved_text
