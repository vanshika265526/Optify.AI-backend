from flask import Flask, request, jsonify
from flask_cors import CORS
import fitz  # PyMuPDF
import cohere
from dotenv import load_dotenv
import os
# Setup Cohere client
load_dotenv()

co = cohere.Client(os.getenv("YOUR_COHERE_API_KEY"))

# Setup Flask
app = Flask(__name__)
CORS(app, resources={r"/analyze": {"origins": ["http://localhost:5173", "https://extraordinary-melba-9ac9bd.netlify.app/"]}})

@app.route('/analyze', methods=['POST'])
def analyze_resume():
    resume = request.files.get('resume')
    jd_text = request.form.get('job_description')

    if not resume or not jd_text:
        return jsonify({"message": "Missing resume or job description"}), 400

    try:
        # Extract resume text
        doc = fitz.open(stream=resume.read(), filetype="pdf")
        resume_text = "".join([page.get_text() for page in doc])

        prompt = f"""
You're an AI resume matcher. Compare the following resume with the job description and give a score (0–99) and tips for improvement. Format like this:
Donot give introductory lines like thank you or anything or conclusion lines.
Resume Match Score: <score%>, <next line>
Tips:
-  1 <next line>
-  2 <next line>
-  3 <next line>
(Keep it clean and detailed tips . No JSON. Make sure every new tip is in new line)

Resume:
{resume_text}

Job Description:
{jd_text}
"""

        response = co.chat(
            message=prompt,
            model="command-light",
            temperature=0,
        )

        raw_text = response.text.strip()
        print("🧠 RAW AI RESPONSE:", raw_text)

        return jsonify({
            "message": raw_text
        })

    except Exception as e:
        print("🔥 Error:", e)
        return jsonify({
            "message": "Something went wrong analyzing the resume."
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
