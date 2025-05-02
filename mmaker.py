
import os
import json
import uuid
from pathlib import Path
from datetime import datetime
from compile_latex import tex_to_pdf
import jinja2

# Use absolute paths for reliability
UPLOAD_FOLDER = Path(__file__).parent / 'outputs'
UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)

def escape_latex(text):
    if not text:
        return ""
    return text.translate(str.maketrans({
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}', '\\': r'\textbackslash{}'
    }))

def generate_autocv(data, preview=False):
    # Build context with LaTeX escaping
    context = {
        'name': escape_latex(data['personal_info']['name']),
        'email': escape_latex(data['personal_info'].get('email', '')),
        'phone': escape_latex(data['personal_info'].get('phone', '')),
        'github': escape_latex(data['personal_info'].get('github', '')),
        'linkedin': escape_latex(data['personal_info'].get('linkedin', '')),
        'summary': escape_latex(data.get('summary', '')),
        'work_experience': data.get('experience', []),
        'projects': data.get('projects', []),
        'education': data.get('education', []),
        'skills': [{'title': key, 'list': data.get('skills', {}).get(key, [])} 
                  for key in data.get('skills', {})]
    }
    
    # Render template
    template_path = Path(__file__).parent / "autoCV_template.tex"
    tex_content = jinja2.Template(template_path.read_text()).render(**context)

    if preview:
        return tex_content

    # Generate unique filename
    file_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"resume_{timestamp}_{file_id}"
    tex_path = UPLOAD_FOLDER / f"{filename}.tex"

    # Save TeX file
    with tex_path.open('w') as f:
        f.write(tex_content)

    # Generate PDF
    try:
        pdf_path = tex_to_pdf(str(tex_path))
        final_pdf = Path(pdf_path)
        print(pdf_path)
        if not final_pdf.exists():
            raise RuntimeError("PDF generation failed - file not created")
            
        return str(final_pdf.absolute())
        
    except Exception as e:
        # Cleanup failed files
        if tex_path.exists():
            tex_path.unlink()
        pdf_path = UPLOAD_FOLDER / f"{filename}.pdf"
        if pdf_path.exists():
            pdf_path.unlink()
        raise

if __name__ == '__main__':
    with open("sample_resume_data.json") as f:
        resume_data = json.load(f)

    # Preview LaTeX
    latex_code = generate_autocv(resume_data, preview=True)
    print("\n===== LATEX OUTPUT =====\n")
    print(latex_code)

    # Generate PDF
    try:
        path = generate_autocv(resume_data)
        print(f"\nPDF generated at: {Path(path).absolute()}")
    except Exception as e:
        print(f"\nError: {str(e)}")




