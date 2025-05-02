import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from resume_parser import extract_text_and_links_from_pdf, ats_extractor, calculate_ats_score
from mmaker import generate_autocv
from pathlib import Path
import logging
import re  # New: for manual cleaning
from pylatexenc.latex2text import LatexNodes2Text  # add import at top if needed

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MIME_TYPES = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def landing():
    """Landing page to choose between Parser and Builder."""
    if 'username' in session:
        return render_template('landing.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    logging.debug("Entering login route")
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            return render_template('login.html', error="Username and password are required")
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[0], password):
            session['username'] = username
            logging.info(f"User {username} logged in")
            return redirect(url_for('landing'))
        logging.warning("Invalid credentials")
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    logging.info("User logged out")
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    logging.debug("Entering signup route")
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            return render_template('signup.html', error="Username and password are required")
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE username = ?", (username,))
        if c.fetchone():
            return render_template('signup.html', error="Username already exists")
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                  (username, generate_password_hash(password)))
        conn.commit()
        conn.close()
        logging.info(f"User {username} signed up")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        logging.warning("Unauthorized access to dashboard")
        return redirect(url_for('login'))
    logging.debug(f"Rendering dashboard for {session['username']}")
    return render_template('dashboard.html')

@app.route('/builder', methods=['GET', 'POST'])
def builder():
    if 'username' not in session:
        logging.warning("Unauthorized access to builder")
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            data = json.loads(request.form['data'])
            preview = request.form.get('preview', 'false').lower() == 'true'
            result = generate_autocv(data, preview)
            return jsonify({'preview': result} if preview else {'download': os.path.basename(result)})
        except Exception as e:
            logging.error(f"Builder error: {e}")
            return jsonify({'error': str(e)}), 500
    return render_template('maker.html')

@app.route('/parser', methods=['GET', 'POST'])
def parser():
    if 'username' not in session:
        logging.warning("Unauthorized access to parser")
        return redirect(url_for('login'))
    logging.debug("Processing resume parser")
    if request.method == 'POST':
        if 'resume' not in request.files:
            return render_template('parser.html', error="No file uploaded")
        file = request.files['resume']
        if file.filename == '':
            return render_template('parser.html', error="No file selected")
        if not file.filename.lower().endswith('.pdf'):
            return render_template('parser.html', error="Only PDF files are allowed")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resume.pdf')
        file.save(file_path)
        resume_text, links = extract_text_and_links_from_pdf(file_path)
        if not resume_text:
            return render_template('parser.html', error="Could not extract text from PDF")
        extracted_data = ats_extractor(resume_text, links)
        score = calculate_ats_score(resume_text, extracted_data)
        return render_template('parser.html', data=extracted_data, score=score)
    return render_template('parser.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            return render_template('forgot_password.html', error="Username is required")
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if not user:
            return render_template('forgot_password.html', error="User not found")
        # In a real app, send a password reset email with a secure token.
        # For simplicity, redirect to reset password page with username.
        return redirect(url_for('reset_password', username=username))
    return render_template('forgot_password.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    username = request.args.get('username', '').strip() if request.method == 'GET' else request.form.get('username', '').strip()
    if not username:
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        new_password = request.form.get('new_password', '').strip()
        if not new_password:
            return render_template('reset_password.html', username=username, error="New password is required")
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        hashed_password = generate_password_hash(new_password)
        c.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, username))
        conn.commit()
        conn.close()
        logging.info(f"Password reset for user {username}")
        return redirect(url_for('login'))
    return render_template('reset_password.html', username=username)

def manual_clean(latex_str):
    # Simple manual cleaning similar to maker.js regex logic
    cleaned = re.sub(r'\\begin\{[^\}]+\}', '', latex_str)
    cleaned = re.sub(r'\\end\{[^\}]+\}', '', cleaned)
    cleaned = re.sub(r'\\[a-zA-Z]+\{([^\}]+)\}', r'\1', cleaned)
    cleaned = re.sub(r'\\[a-zA-Z]+\s?', '', cleaned)
    cleaned = re.sub(r'[\$\\]', '', cleaned)
    return cleaned.strip()

def convert_latex_to_plain_text(latex_str):
    import re
    try:
        # Attempt to extract content between \begin{document} and \end{document}
        match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', latex_str, re.DOTALL)
        content = match.group(1) if match else latex_str
    except Exception as e:
        logging.error("Error extracting document environment from LaTeX.", exc_info=True)
        content = latex_str
    try:
        return LatexNodes2Text().latex_to_text(content).strip()
    except Exception as e:
        logging.error("Error converting LaTeX to plain text using pylatexenc.", exc_info=True)
        return manual_clean(content)

@app.route('/preview', methods=['POST'])
def preview():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data = json.loads(request.form['data'])
        preview_code = generate_autocv(data, preview=True)
        logging.debug(f"Generated preview LaTeX code: {preview_code}")
        plain_preview = convert_latex_to_plain_text(preview_code)
        return jsonify({"preview": plain_preview})
    except Exception as e:
        logging.error("Error in /preview endpoint.", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/preview_html', methods=['POST'])
def preview_html():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    try:
        data = json.loads(request.form['data'])
        # Render HTML preview using a dedicated template
        html_preview = render_template('preview_resume.html', data=data)
        return jsonify({"preview": html_preview})
    except Exception as e:
        logging.error("Error generating HTML preview", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filetype>')
def download(filetype):
    if 'username' not in session:
        logging.warning("Unauthorized access to download")
        return redirect(url_for('login'))
    
    if filetype != 'pdf':
        logging.error(f"Invalid file type requested: {filetype}")
        return "Only PDF downloads are supported", 400
    
    file_path = Path(app.config['UPLOAD_FOLDER']) / 'resume.pdf'
    logging.info(f"Attempting to download: {file_path}")
    
    if not file_path.is_file():
        logging.error(f"File not found: {file_path}")
        return "Resume file not found. Please generate the resume first.", 404
    
    try:
        return send_file(
            file_path,
            mimetype=MIME_TYPES.get(filetype, 'application/octet-stream'),
            as_attachment=True,
            download_name=f"resume.{filetype}"
        )
    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return f"Error downloading file: {str(e)}", 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)