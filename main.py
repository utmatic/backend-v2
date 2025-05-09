from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
import fitz  # PyMuPDF
import re

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

def generate_utm_url(base_url, item_number, source, medium, campaign):
    return f"{base_url}{item_number}?utm_source={source}&utm_medium={medium}&utm_campaign={campaign}&utm_content={item_number}"

def find_matches(text, regex):
    return re.findall(regex, text)

@app.route('/process', methods=['POST'])
def process_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF uploaded'}), 400

    pdf_file = request.files['pdf']
    filename = secure_filename(pdf_file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    pdf_file.save(pdf_path)

    mode = request.form.get('mode')
    base_url = request.form.get('base_url', '')
    item_format = request.form.get('item_format', '')
    source = request.form.get('utm_source')
    medium = request.form.get('utm_medium')
    campaign = request.form.get('utm_campaign')

    item_regex = item_format.replace('N', '\d').replace('L', '[A-Za-z]')
    compiled_regex = re.compile(item_regex)

    doc = fitz.open(pdf_path)
    changes = []

    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        matches = compiled_regex.findall(text)

        for match in matches:
            search_instances = page.search_for(match, hit_max=20)
            if not search_instances:
                continue
            for inst in search_instances:
                url = generate_utm_url(base_url, match, source, medium, campaign)
                page.insert_link({
                    "from": inst,
                    "uri": url,
                    "kind": fitz.LINK_URI,
                })
                changes.append(f"Added hyperlink to '{match}' on page {page_num + 1}")

    processed_path = pdf_path.replace('.pdf', '-processed.pdf')
    doc.save(processed_path)
    doc.close()

    return send_file(processed_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)