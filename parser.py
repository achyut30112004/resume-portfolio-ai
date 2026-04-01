import pdfplumber
import re

def extract_text(file_path):
    """Extract raw text from PDF using pdfplumber."""
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print("Error reading PDF:", e)
    return text


def parse_resume(file_path):
    text = extract_text(file_path)

    sections = {
        "Education": [],
        "Experience": [],
        "Skills": []
    }

    current_section = None

    for line in text.splitlines():
        line_clean = line.strip()

        if re.match(r"(Education|Academics)", line_clean, re.IGNORECASE):
            current_section = "Education"
        elif re.match(r"(Experience|Internship|Projects|Work)", line_clean, re.IGNORECASE):
            current_section = "Experience"
        elif re.match(r"(Skills|Technical Skills|Abilities)", line_clean, re.IGNORECASE):
            current_section = "Skills"
        elif current_section and line_clean:
            sections[current_section].append(line_clean)

    # Filter junk % values
    sections["Skills"] = [item for item in sections["Skills"] if not re.search(r"\d+%|\d+\.\d+", item)]

    email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone = re.search(r"\+?\d[\d \-]{8,}", text)

    name = text.split("\n")[0].strip()

    return {
        "name": name,
        "email": email.group(0) if email else "Not found",
        "phone": phone.group(0) if phone else "Not found",
        "education": sections["Education"],
        "experience": sections["Experience"],
        "skills": sections["Skills"],
    }