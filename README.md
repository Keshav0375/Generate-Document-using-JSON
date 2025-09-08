# Resume Generator

A modular, optimized Python application to generate professionally formatted Word documents and PDFs from JSON data.

## Features

- **JSON-based content management** - Edit resume content in structured JSON format
- **Word document generation** - Creates properly formatted .docx files
- **PDF conversion** - Automatic PDF generation from Word documents
- **Streamlit web interface** - User-friendly GUI for editing and generating resumes
- **Command-line interface** - Generate resumes directly from terminal
- **Customizable formatting** - Adjust margins, fonts, and spacing
- **Error handling** - Robust error handling and logging
- **Modular design** - Clean, maintainable code structure

## Installation

### Prerequisites
- Python 3.8+
- Microsoft Word (optional, for better PDF conversion on Windows/Mac)

### Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run setup script:
   ```bash
   python setup.py
   ```

## Usage

### Web Interface (Streamlit)
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

### Command Line
```bash
# Basic usage
python run.py resume_data.json

# Custom output directory
python run.py resume_data.json -o ./my_resumes

# Custom filename
python run.py resume_data.json -n john_doe_resume

# Word only (skip PDF)
python run.py resume_data.json --word-only

# Custom margins and font
python run.py resume_data.json --margin-top 0.7 --font Arial --font-size 12
```

### Python API
```python
from resume_generator import ResumeGenerator, DocumentConfig

# Configure document settings
config = DocumentConfig(
    margin_top=0.5,
    margin_bottom=0.5,
    font_name="Calibri",
    font_size_normal=11
)

# Create generator
generator = ResumeGenerator(config)

# Generate resume
word_path, pdf_path = generator.generate_from_json(
    "resume_data.json",
    output_dir="./output",
    base_name="my_resume"
)
```

## JSON Structure

The resume data should follow this structure:

```json
{
  "header": {
    "name": "Full Name",
    "phone": "123-456-7890",
    "email": "email@example.com",
    "location": "City, State",
    "linkedin": "https://linkedin.com/in/username",
    "portfolio": "https://portfolio.com",
    "github": "https://github.com/username"
  },
  "technical_skills": {
    "Languages": "Python, Java, C++",
    "Databases": "MySQL, PostgreSQL, MongoDB",
    "Frameworks": "Django, React, FastAPI"
  },
  "education": [
    {
      "degree": "Master of Science in Computer Science",
      "school": "University Name",
      "location": "City, State",
      "dates": "Jan 2020 - Dec 2022",
      "gpa": "3.8/4.0",
      "notes": ["Dean's List", "Research Assistant"]
    }
  ],
  "experience": [
    {
      "title": "Software Engineer",
      "company": "Company Name",
      "location": "City, State",
      "dates": "Jan 2023 - Present",
      "bullets": [
        "Developed feature X resulting in Y improvement",
        "Led team of Z engineers on project A"
      ]
    }
  ],
  "projects": [...],
  "competitions": [...],
  "certifications": [...]
}
```

## Project Structure

```
resume-generator/
├── resume_generator.py    # Core resume generation module
├── app.py                 # Streamlit web application
├── run.py                 # Command-line interface
├── setup.py              # Setup and installation script
├── requirements.txt      # Python dependencies
├── resume_data.json      # Sample/default resume data
├── output/              # Generated resumes directory
└── README.md            # Documentation
```

## Features in Detail

### Document Configuration
- Customizable page margins
- Multiple font options
- Adjustable font sizes
- Line and paragraph spacing control

### Error Handling
- JSON validation
- File I/O error handling
- Graceful PDF generation fallback
- Comprehensive logging

### Modular Architecture
- `DocumentConfig`: Configuration dataclass
- `ResumeFormatter`: Formatting utilities
- `ResumeBuilder`: Document construction
- `ResumeGenerator`: Main generation logic
- `ResumeApp`: Streamlit interface

## Troubleshooting

### PDF Generation Issues
If PDF generation fails:
1. Ensure Microsoft Word is installed (Windows/Mac)
2. On Linux, install LibreOffice: `sudo apt-get install libreoffice`
3. Use `--word-only` flag to skip PDF generation

### Font Issues
If fonts don't appear correctly:
1. Ensure the font is installed on your system
2. Use standard fonts like Calibri, Arial, or Times New Roman

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

MIT License - feel free to use this project for personal or commercial purposes.
