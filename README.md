# Resume Website

This project is a comprehensive web application for building and parsing resumes using Flask, seamlessly integrating LaTeX for high-quality PDF generation and leveraging the Google Generative AI API for advanced resume parsing.

## Setup Instructions

1. Clone the repository and navigate to the project directory.
2. Create a virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database and run the application:
   ```bash
   python app.py
   ```
5. Open your browser at [http://localhost:5000](http://localhost:5000).

## Project Structure

- `app.py`: Main Flask application.
- `templates/`: HTML templates for rendering pages.
- `static/`: CSS, JavaScript, and other assets.
- `uploads/`: Folder for uploaded files.
- `config.yaml`: Configuration file containing API keys and other settings.
- `requirements.txt`: Python dependencies.
- `README.md`: Project documentation.

## Features

- **Resume Builder**: Customize and generate resume previews in real time.
- **Resume Parser**: Upload and extract resume details from PDF files.
- **API Integration**: Utilizes the Google Generative AI API to enhance parsing and preview generation.
- **LaTeX Generation**: Automatically creates LaTeX source files that can be compiled into professional PDF resumes.
- **User Authentication**: Secure sign-up and login functionalities.
- **Responsive Design**: Optimized for both desktop and mobile devices.

## API and Configuration

- The application integrates with the Google Generative AI API.
- API key is stored in `config.yaml` under the key `GENAI_API_KEY`; make sure you update this with your valid API key.
- Additional settings such as database connection strings, debugging options, and other environment variables are managed in `config.yaml`.

## Detailed Usage

- **Authentication**: Register a new account or log in to access both builder and parser features.
- **Resume Builder**:
  - Input your personal details and select a resume template.
  - Preview the generated resume and download it as a PDF.
- **Resume Parser**:
  - Upload a PDF resume to extract details.
  - The parsed data can be reviewed and edited within the builder.
- **LaTeX Compilation**:
  - The application produces `.tex` files that can be compiled using any standard TeX distribution (e.g., `pdflatex`, `xelatex`, or `latexmk`).

## Development and Contribution

- **Local Development**:
  - Ensure you are using Python 3.8 or later.
  - Activate the virtual environment and install dependencies as detailed above.
  - Start the application using `python app.py`.
- **Testing**:
  - Automated tests (if available) are placed under the `tests/` directory.
  - Use a test runner like `pytest` to run the tests.
- **Contributing**:
  - Fork the repository and create a new branch for your changes.
  - Follow the coding standards and include tests with your contributions.
  - Submit a pull request for review.

## Troubleshooting

- **Virtual Environment Issues**: Confirm you are activating the correct environment and using the appropriate shell.
- **Dependency Errors**: If installation fails, double-check your Python version and ensure `pip install -r requirements.txt` completes without errors.
- **API Key Problems**: Verify that `config.yaml` holds a valid `GENAI_API_KEY`.
- **LaTeX Compilation**: Ensure a full TeX distribution (such as TeX Live or MiKTeX) is installed on your system.
- **Application Errors**: Check terminal output for error messages when running `app.py` and consult logs for further debugging information.