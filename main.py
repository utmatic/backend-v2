from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import tempfile
import fitz  # PyMuPDF
import re
import io
import zipfile

app = Flask(__name__)
CORS(app)

app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

def generate_utm_url(base_url, item_number, source, medium, campaign):
    return f"{base_url}{item_number}?utm_source={source}&utm_medium={medium}&utm_campaign={campaign}&utm_content={item_number}"

def get_matches_from_words(words, item_regex):
    matches = []
    for i in range(len(words)):
        for j in range(i+1, min(i+6, len(words))+1):
            joined_text = ''.join([w[4] for w in words[i:j]])
            if re.fullmatch(item_regex, joined_text):
                rect = fitz.Rect(words[i][0], words[i][1], words[j-1][2], words[j-1][3])
                matches.append((joined_text, rect))
    return matches

@app.route('/process', methods=['POST'])
def process_pdf():
    debug_log = {
        "matches_found": [],
        "links_inserted": [],
        "errors": []
    }

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

    for page_num, page in enumerate(doc):
        if mode == 'utm-only':
            links = page.get_links()
            for link in links:
                if 'uri' in link:
                    orig_url = link['uri']
                    if '?' in orig_url:
                        new_url = orig_url + f"&utm_source={source}&utm_medium={medium}&utm_campaign={campaign}&utm_content={orig_url}"
                    else:
                        new_url = orig_url + f"?utm_source={source}&utm_medium={medium}&utm_campaign={campaign}&utm_content={orig_url}"
                    try:
                        page.insert_link({
                            "from": link["from"],
                            "uri": new_url,
                            "kind": fitz.LINK_URI,
                        })
                        debug_log["links_inserted"].append(f"Updated link on page {page_num+1}")
                    except Exception as e:
                        debug_log["errors"].append(f"Failed to update link on page {page_num+1}: {str(e)}")
        elif mode == 'hyperlink-utm':
            words = page.get_text("words")
            matches = get_matches_from_words(words, compiled_regex)

            for match_text, rect in matches:
                debug_log["matches_found"].append(f"Page {page_num+1}: {match_text}")
                try:
                    url = generate_utm_url(base_url, match_text, source, medium, campaign)
                    page.insert_link({
                        "from": rect,
                        "uri": url,
                        "kind": fitz.LINK_URI,
                    })
                    debug_log["links_inserted"].append(f"Linked {match_text} on page {page_num+1}")
                except Exception as e:
                    debug_log["errors"].append(f"Failed to link {match_text} on page {page_num+1}: {str(e)}")

    processed_path = pdf_path.replace('.pdf', '-processed.pdf')
    doc.save(processed_path)
    doc.close()

    # Return the processed PDF and debug log in a zip
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zf:
        zf.write(processed_path, arcname=os.path.basename(processed_path))
        zf.writestr("debug-log.json", str(debug_log).replace("'", '"'))

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='debug-output.zip')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)