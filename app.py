from flask import Flask, render_template, request
from transformers import pipeline
import pdfplumber
import docx
import os

app = Flask(__name__)

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to extract text from a PDF
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text

# Function to extract text from a Word document
def extract_text_from_word(word_path):
    doc = docx.Document(word_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Function to handle text input
def extract_text_from_text_file(txt_path):
    with open(txt_path, "r") as file:
        return file.read()

# Route to home page
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        file_ext = file.filename.split(".")[-1].lower()

        # Save file
        file_path = os.path.join("uploads", file.filename)
        file.save(file_path)

        # Extract text based on file type
        if file_ext == "pdf":
            text = extract_text_from_pdf(file_path)
        elif file_ext == "docx":
            text = extract_text_from_word(file_path)
        elif file_ext == "txt":
            text = extract_text_from_text_file(file_path)
        else:
            return "Unsupported file format", 400

        # Summarize the text
        summary = summarizer(text, max_length=500, min_length=100, do_sample=False)
        return render_template("index.html", summary=summary[0]['summary_text'], original_text=text[:2000])

    return render_template("index.html", summary=None)

if __name__ == "__main__":
    app.run(debug=True)
