from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
import fitz  # PyMuPDF
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

def generate_utm_url(base_url, item_number, source, medium, campaign):
    return f"{base_url}{item_number}?utm_source={source}&utm_medium={medium}&utm_campaign={campaign}&utm_content={item_number}"

def find_matches(text, pattern):
    return re.findall(pattern, text)

@app.route('/process', methods=['POST'])
def process_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF uploaded'}), 400

    pdf_file = request.files['pdf']
    filename = secure_filename(pdf_file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    pdf_file.save(pdf_path)

    mode = request.form.get('mode')  # "utm-only" or "hyperlink-utm"
    base_url = request.form.get('base_url', '')
    item_format = request.form.get('item_format', '')
    source = request.form.get('utm_source')
    medium = request.form.get('utm_medium')
    campaign = request.form.get('utm_campaign')

    doc = fitz.open(pdf_path)
    changes = []

    item_regex = item_format.replace('N', '\d').replace('L', '[A-Za-z]')

    for page_num, page in enumerate(doc):
        text = page.get_text()
        if mode == 'utm-only':
            links = page.get_links()
            for link in links:
                if 'uri' in link:
                    orig_url = link['uri']
                    if '?' in orig_url:
                        new_url = orig_url + f"&utm_source={source}&utm_medium={medium}&utm_campaign={campaign}&utm_content={orig_url}"
                    else:
                        new_url = orig_url + f"?utm_source={source}&utm_medium={medium}&utm_campaign={campaign}&utm_content={orig_url}"
                    page.insert_link({
                        "from": link["from"],
                        "uri": new_url,
                        "kind": fitz.LINK_URI,
                    })
                    changes.append(f"Updated link on page {page_num+1}")
        elif mode == 'hyperlink-utm':
            matches = find_matches(text, item_regex)
            for match in matches:
                for inst in page.search_for(match):
                    url = generate_utm_url(base_url, match, source, medium, campaign)
                    page.insert_link({
                        "from": inst,
                        "uri": url,
                        "kind": fitz.LINK_URI,
                    })
                    changes.append(f"Added link to {match} on page {page_num+1}")

    processed_path = pdf_path.replace('.pdf', '-processed.pdf')
    doc.save(processed_path)
    doc.close()

    return send_file(processed_path, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)