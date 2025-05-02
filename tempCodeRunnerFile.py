import subprocess

def tex_to_pdf(tex_file_path, output_dir="."):
    try:
        # Run pdflatex to compile the .tex file to PDF
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",  # Suppress interactive prompts
                f"-output-directory={output_dir}",
                tex_file_path
            ],
            check=True,  # Raise error if command fails
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"PDF generated successfully in {output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {tex_file_path} to PDF:")
        print(e.stderr.decode())

# Example usage:
tex_to_pdf("test.tex", output_dir="./output")