import subprocess
import os
from pathlib import Path

def tex_to_pdf(tex_file_path):
    """
    Converts a .tex file to PDF with explicit path handling and validation
    """
    tex_path = Path(tex_file_path).absolute()
    if not tex_path.exists():
        raise FileNotFoundError(f"TeX file not found: {tex_path}")

    working_dir = tex_path.parent
    pdf_name = f"{tex_path.stem}.pdf"
    pdf_path = working_dir / pdf_name

    # Clean existing PDF if present
    if pdf_path.exists():
        os.remove(pdf_path)

    # Run compilation with explicit output handling
    commands = [
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
         f"-output-directory={working_dir}", tex_path.name],
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
         f"-output-directory={working_dir}", tex_path.name]
    ]

    for cmd in commands:
        process = subprocess.run(
            cmd,
            cwd=str(working_dir),
            capture_output=True,
            text=True
        )
        if process.returncode != 0:
            error_log = process.stderr or process.stdout
            raise RuntimeError(f"LaTeX Error:\n{error_log}")

    if not pdf_path.exists():
        raise RuntimeError(f"PDF generation failed. Expected at: {pdf_path}")
    
    return str(pdf_path)




















