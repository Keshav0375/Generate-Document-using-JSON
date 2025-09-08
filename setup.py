#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Setup script for Resume Generator
Handles installation and initial configuration
'''

import os
import sys
import subprocess
import json
from pathlib import Path


def create_requirements_file():
    '''Create requirements.txt file'''
    requirements = '''streamlit>=1.28.0
python-docx>=1.1.0
docx2pdf>=0.1.8
Pillow>=10.0.0
'''

    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    print("Created requirements.txt")


def install_dependencies():
    '''Install required packages'''
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)


def create_directory_structure():
    '''Create necessary directories'''
    directories = ['output', 'templates', 'data']
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
    print("Created directory structure")


def create_sample_json():
    '''Create sample resume JSON if it doesn't exist'''
    sample_data = {
        "header": {
            "name": "John Doe",
            "phone": "555-123-4567",
            "email": "john.doe@email.com",
            "location": "New York, NY",
            "linkedin": "https://linkedin.com/in/johndoe",
            "portfolio": "https://johndoe.dev",
            "github": "https://github.com/johndoe"
        },
        "technical_skills": {
            "Languages": "Python, JavaScript, Java, C++",
            "Frameworks": "React, Node.js, Django, FastAPI",
            "Databases": "PostgreSQL, MongoDB, Redis",
            "Tools": "Git, Docker, AWS, Jenkins"
        },
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "school": "University of Technology",
                "location": "New York, NY",
                "dates": "Sep 2018 - May 2022",
                "gpa": "3.8/4.0",
                "notes": ["Dean's List", "Computer Science Club President"]
            }
        ],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Tech Corp",
                "location": "New York, NY",
                "dates": "Jun 2022 - Present",
                "bullets": [
                    "Developed full-stack web applications serving 10,000+ users",
                    "Improved system performance by 40% through database optimization",
                    "Led team of 3 junior developers on key product features"
                ]
            }
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "technologies": "React, Node.js, PostgreSQL",
                "dates": "Jan 2022 - May 2022",
                "bullets": [
                    "Built responsive e-commerce platform with payment integration",
                    "Implemented user authentication and admin dashboard"
                ]
            }
        ],
        "competitions": [
            {
                "name": "ACM Programming Contest",
                "result": "Regional Finalist",
                "date": "2021"
            }
        ],
        "certifications": [
            {
                "name": "AWS Certified Solutions Architect",
                "date": "2023"
            }
        ]
    }
    
    if not os.path.exists('resume_data.json'):
        with open('resume_data.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2)
        print("Created sample resume_data.json")
    else:
        print("resume_data.json already exists")


def main():
    print("Setting up Resume Generator...")
    print("-" * 40)

    # Create requirements file
    create_requirements_file()

    # Install dependencies
    response = input("Install dependencies? (y/n): ").lower()
    if response == 'y':
        install_dependencies()

    # Create directory structure
    create_directory_structure()

    # Create sample JSON
    create_sample_json()

    print("-" * 40)
    print("Setup complete!")
    print("\nTo run the application:")
    print("  streamlit run app.py")
    print("\nTo generate resume from command line:")
    print("  python resume_generator.py")


if __name__ == "__main__":
    main()
