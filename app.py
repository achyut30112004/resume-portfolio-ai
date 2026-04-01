# app.py
"""
Streamlit front-end for:
 - resume parsing (parser.parse_resume)
 - AI resume improvement (ats.improve_resume) [Gemini / google.generativeai]
 - HTML portfolio generation (portfolio_generator.generate_portfolio)

Requirements:
 - streamlit
 - python-docx / pdfplumber etc (for parser.py)
 - google-generative-ai (if using Gemini) and configure GOOGLE_API_KEY in your shell
 - jinja2 (for portfolio_generator)

Set your Google API key in ~/.zshrc or environment:
export GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
Then reload shell: source ~/.zshrc
"""

import os
import json
import tempfile
import traceback

import streamlit as st

# Import your project modules (make sure these files exist)
# parser.parse_resume(file_path) -> returns dict
# ats.improve_resume(resume_text) -> returns JSON/text (string)
# portfolio_generator.generate_portfolio(data) -> returns path to HTML file
try:
    from parser import parse_resume
except Exception:
    parse_resume = None

try:
    import ats  # your ats.py (uses google.generativeai)
except Exception:
    ats = None

try:
    import portfolio_generator
except Exception:
    portfolio_generator = None


st.set_page_config(page_title="Resume → Portfolio AI", layout="wide")
st.title("Resume → Portfolio AI")

if parse_resume is None:
    st.error("parser.py not found or import failed. Make sure parser.py exists and is importable.")
    st.stop()

uploaded = st.file_uploader("Upload resume (PDF or DOCX)", type=["pdf", "docx"], accept_multiple_files=False)

# helper to save uploaded to a temporary file
def _save_upload_to_temp(uploaded_file):
    suffix = ""
    if uploaded_file.type == "application/pdf" or uploaded_file.name.lower().endswith(".pdf"):
        suffix = ".pdf"
    elif uploaded_file.name.lower().endswith(".docx"):
        suffix = ".docx"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded_file.getbuffer())
    tmp.flush()
    tmp.close()
    return tmp.name


st.sidebar.header("Environment")
st.sidebar.write("GOOGLE_API_KEY set?" )
st.sidebar.write(f"`{'Set' if os.getenv('GOOGLE_API_KEY') else 'Not set'}`")

if uploaded:
    # save to temp path for parser
    try:
        tmp_path = _save_upload_to_temp(uploaded)
    except Exception as e:
        st.error("Failed to save uploaded file: " + str(e))
        st.stop()

    st.markdown("### Extracted Data Preview")
    try:
        data = parse_resume(tmp_path)  # parser should return dict with keys: name, skills, experience, education...
    except Exception as e:
        st.error("Error while parsing resume:")
        st.code(traceback.format_exc(), language="text")
        data = None

    if data:
        st.json(data)

        # Download JSON
        st.download_button("Download extracted JSON", data=json.dumps(data, indent=2), file_name="resume_data.json", mime="application/json")

        # Improve resume with AI
        if ats is None:
            st.warning("ats.py not found or import failed — AI resume improvement disabled.")
        else:
            st.markdown("---")
            st.subheader("🔧 Improve resume (AI)")
            # create plain text version of resume_text for improvement
            # join most fields into a reasonably formatted string
            def _make_resume_text(d: dict):
                parts = []
                for k in ["name", "email", "phone", "summary", "skills", "experience", "education"]:
                    v = d.get(k)
                    if v:
                        if isinstance(v, list):
                            parts.append(f"{k}:\n" + "\n".join(map(str, v)))
                        else:
                            parts.append(f"{k}: {v}")
                # if parser uses different keys, include full dict as fallback
                if not parts:
                    parts.append(json.dumps(d, indent=2))
                return "\n\n".join(parts)

            resume_text = _make_resume_text(data)

            st.text_area("Resume text sent to AI (you can edit before sending)", value=resume_text, height=200, key="resume_text_area")

            if st.button("Improve Resume with Gemini AI"):
                with st.spinner("Sending to Gemini... (make sure GOOGLE_API_KEY is set)"):
                    try:
                        # call ats.improve_resume — should return text (JSON formatted string)
                        improved = ats.improve_resume(st.session_state["resume_text_area"])
                        # try to show as JSON if possible
                        try:
                            parsed = json.loads(improved)
                            st.success("AI returned JSON result:")
                            st.json(parsed)
                            st.download_button("Download improved JSON", data=json.dumps(parsed, indent=2), file_name="improved_resume.json", mime="application/json")
                        except Exception:
                            st.success("AI returned text:")
                            st.code(improved, language="text")
                            st.download_button("Download improved text", data=improved, file_name="improved_resume.txt", mime="text/plain")
                    except Exception:
                        st.error("AI improvement failed. See traceback below:")
                        st.code(traceback.format_exc(), language="text")

        # Portfolio generation
        st.markdown("---")
        st.subheader("🌐 Generate portfolio HTML")

        if portfolio_generator is None:
            st.warning("portfolio_generator.py missing or import failed — portfolio generation disabled.")
        else:
            if st.button("Create Portfolio HTML"):
                with st.spinner("Generating portfolio..."):
                    try:
                        # portfolio_generator.generate_portfolio expects JSON/dict and returns path to generated HTML file
                        file_path = portfolio_generator.generate_portfolio(data)
                        # read and display file
                        with open(file_path, "r", encoding="utf-8") as f:
                            html_code = f.read()
                        st.success("Portfolio created successfully!")
                        st.download_button("Download Portfolio HTML", data=html_code, file_name="portfolio.html", mime="text/html")
                        st.markdown("### Preview:")
                        st.components.v1.html(html_code, height=700, scrolling=True)
                    except Exception:
                        st.error("Portfolio generation failed:")
                        st.code(traceback.format_exc(), language="text")

    # cleanup: leave tmp_path for debugging; if you want immediate cleanup uncomment below
    # try:
    #     os.remove(tmp_path)
    # except Exception:
    #     pass

else:
    st.info("Upload a resume (PDF or DOCX) from the left to begin.")
    st.write("This demo will parse your resume, let you improve it using Gemini, and generate a simple HTML portfolio.")

# Footer / troubleshooting tips
st.markdown("---")
st.write("Troubleshooting:")
st.write("- Make sure `GOOGLE_API_KEY` is set in your environment (`export GOOGLE_API_KEY=...`), then restart Streamlit.")
st.write("- If AI fails, check terminal for error messages and confirm `google-generative-ai` is installed and working.")
