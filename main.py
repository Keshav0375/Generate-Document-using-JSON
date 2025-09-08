"""
Quick Start Script for Resume Generator
Main entry point for the application with all features integrated
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = {
        'docx': 'python-docx',
        'docx2pdf': 'docx2pdf',
        'streamlit': 'streamlit'
    }

    missing = []
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        print("⚠️ Missing dependencies detected!")
        print(f"Please install: {', '.join(missing)}")
        print(f"\nRun: pip install {' '.join(missing)}")
        return False

    return True


def create_project_structure():
    """Create necessary directories and files"""
    directories = ['output', 'backups', 'templates', 'data']

    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)

    print("✅ Project structure created")


def create_sample_resume_json():
    """Create a sample resume JSON file if it doesn't exist"""
    resume_data = {
        "header": {
            "name": "Keshav Arri",
            "phone": "647-227-1538",
            "email": "arri@uwindsor.ca",
            "location": "Ontario, Canada",
            "linkedin": "https://linkedin.com/in/keshav-arri",
            "portfolio": "https://keshavarri.com",
            "github": "https://github.com/keshavarri"
        },
        "technical_skills": {
            "Languages": "Python, SQL, C/C++, Java, Bash/Shell Scripting, HTML, CSS",
            "Databases": "MySQL, PostgreSQL, MongoDB, Pinecone, Weaviate, Milvus, Snowflake, Redis",
            "AI/ML": "PyTorch, TensorFlow, XGBoost, Hugging Face, LangChain, LangGraph, OpenCV, RAG",
            "Cloud/Dev": "AWS, Azure, GCP, Docker, FastAPI, React, Git, CI/CD Pipelines, RESTful APIs",
            "Related skills": "ETL Pipelines, Fine-tuning LLMs, Prompt Engineering, Data Modelling, A/B Testing, NER, OCR, Socket Programming, Data Structures & Algorithms"
        },
        "education": [
            {
                "degree": "Master of Applied Computing — Specialization: Artificial Intelligence",
                "school": "University of Windsor",
                "location": "Ontario, Canada",
                "dates": "Jan 2025 - Present",
                "gpa": "",
                "notes": ["Final Semester Requires a 4 to 8 months Internship Starting Jan 2026"]
            },
            {
                "degree": "Bachelor of Technology in Computer Science and Engineering",
                "school": "Guru Nanak Dev Engineering College",
                "location": "Punjab, India",
                "dates": "Sep 2020 - Sep 2024",
                "gpa": "SGPA 8.13/10",
                "notes": []
            }
        ],
        "experience": [
            {
                "title": "AI ML Engineer",
                "company": "Slideoo",
                "location": "Bangalore, India",
                "dates": "Feb 2024 - Feb 2025",
                "bullets": [
                    "Engineered multimodal pipeline converting text, documents, websites and YouTube URLs into PowerPoint presentations, achieving 83%-time reduction to 30 seconds vs competitor's 3-min turnaround, helping secure seed funding.",
                    "Scaled system to handle 10x traffic growth by implementing distributed architecture using OpenAI GPT and Claude model with multi-threading across Azure Web Apps, AWS Lambda and Bedrock, achieving 99% uptime.",
                    "Improved LLM response accuracy by 25% and reduced API costs by 40% through optimized prompt engineering, few-shot learning and intelligent caching strategy using Redis and MongoDB for frequently accessed templates.",
                    "Led a 4-member intern team to develop a prompt-based research report generation that automated 70% of manual research tasks using chain-of-thought reasoning."
                ]
            },
            {
                "title": "Data Scientist & NLP Researcher",
                "company": "Sabudh Foundation",
                "location": "Punjab, India",
                "dates": "Jul 2023 - Jan 2024",
                "bullets": [
                    "Automated 60% of manual document processing by developing intelligent OCR pipeline using Detectron2, spaCy NLP, and custom entity recognition, processing 10,000+ documents monthly with 94% accuracy.",
                    "Achieved 91%-line segmentation accuracy on damaged ancient manuscripts successfully digitizing 10,000+ historical documents for preservation project.",
                    "Collaborated with 8-member research team to document and present solutions to government officials, demonstrating 3x faster processing than existing solutions."
                ]
            }
        ],
        "projects": [
            {
                "name": "DataDialect AI",
                "description": "Talk to any database using natural language",
                "dates": "Apr 2025 – Jul 2025",
                "bullets": [
                    "Achieved 89% query accuracy on complex multi-table joins by implementing NL2SQL system using few-shot learning and semantic similarity matching.",
                    "Reduced database query time by 65% for non-technical users, eliminating need for SQL knowledge and saving 10+ hours weekly for business analysts.",
                    "Integrated with 4 database types (MySQL, PostgreSQL, MongoDB, Vector Databases)"
                ]
            },
            {
                "name": "Stanford STORM API Wrapper",
                "description": "Knowledge curation system",
                "dates": "Jan 2025 – Mar 2025",
                "bullets": [
                    "Wrapped Stanford STORM research pipeline into REST API using multi-LLM orchestration (GPT-4/Claude) via LangChain, handling 500+ daily requests with streaming responses.",
                    "Reduced deployment time by 75% through Docker containerization and FastAPI async endpoints, enabling researchers to generate comprehensive reports in 5 minutes vs 20 minutes."
                ]
            }
        ],
        "competitions": [
            {
                "name": "CS Demo Day Participant",
                "organization": "University of Windsor",
                "location": "Windsor, ON",
                "date": "Apr 2025",
                "bullets": ["Showcased EduMetrics project to 200+ industry professionals and academic faculty."]
            },
            {
                "name": "WinHacks 2025",
                "organization": "University of Windsor",
                "location": "Windsor, ON",
                "date": "Jan 2025",
                "bullets": ["Prototyped AI-powered solution in 48-hour hackathon emphasizing rapid prototyping skills."]
            }
        ],
        "certifications": [
            {"name": "Dataiku Advance Designer, Developer Certificate, ML Practitioner", "date": "Feb 2025"},
            {"name": "Google Data Analytics Professional Certificate – Coursera", "date": "Dec 2024"},
            {"name": "Selenium Essential Training - LinkedIn Learning", "date": "Oct 2024"},
            {"name": "Microsoft Power BI Desktop for Business Intelligence – Udemy", "date": "Mar 2023"},
            {"name": "TCS iON Career Edge - Soft Skills Development", "date": "Feb 2023"}
        ]
    }

    if not os.path.exists('resume_data.json'):
        with open('resume_data.json', 'w', encoding='utf-8') as f:
            json.dump(resume_data, f, indent=2)
        print("✅ Created sample resume_data.json")
        return True
    else:
        print("ℹ️ resume_data.json already exists")
        return False


def quick_generate():
    """Quick generation of resume with default settings"""
    try:
        from resume_generator import ResumeGenerator, DocumentConfig

        # Check if JSON exists
        if not os.path.exists('resume_data.json'):
            print("❌ resume_data.json not found. Creating sample...")
            create_sample_resume_json()

        # Create generator with default config
        config = DocumentConfig()
        generator = ResumeGenerator(config)

        # Generate resume
        print("📄 Generating resume...")
        word_path, pdf_path = generator.generate_from_json(
            'resume_data.json',
            output_dir='./output',
            base_name='resume'
        )

        print("✅ Resume generated successfully!")
        print(f"📄 Word: {word_path}")
        if pdf_path:
            print(f"📄 PDF: {pdf_path}")
        else:
            print("⚠️ PDF generation failed (docx2pdf may not be installed)")

        return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def run_web_interface():
    """Launch the Streamlit web interface"""
    try:
        import streamlit.web.cli as stcli
        sys.argv = ["streamlit", "run", "app.py"]
        stcli.main()
    except ImportError:
        print("❌ Streamlit not installed. Please run: pip install streamlit")
        return False


def run_cli_interface():
    """Run the command-line interface"""
    from resume_generator import ResumeGenerator, DocumentConfig
    from utils import JSONValidator, BackupManager, StatisticsGenerator

    parser = argparse.ArgumentParser(
        description='Resume Generator - Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'action',
        choices=['generate', 'validate', 'backup', 'stats', 'clean'],
        help='Action to perform'
    )

    parser.add_argument(
        '-i', '--input',
        default='resume_data.json',
        help='Input JSON file (default: resume_data.json)'
    )

    parser.add_argument(
        '-o', '--output',
        default='./output',
        help='Output directory (default: ./output)'
    )

    parser.add_argument(
        '-n', '--name',
        default='resume',
        help='Output filename base (default: resume)'
    )

    parser.add_argument(
        '--word-only',
        action='store_true',
        help='Generate only Word document (skip PDF)'
    )

    args = parser.parse_args()

    if args.action == 'generate':
        # Generate resume
        config = DocumentConfig()
        generator = ResumeGenerator(config)

        try:
            if args.word_only:
                with open(args.input, 'r') as f:
                    data = json.load(f)
                word_path = os.path.join(args.output, f"{args.name}.docx")
                generator.generate_word(data, word_path)
                print(f"✅ Generated: {word_path}")
            else:
                word_path, pdf_path = generator.generate_from_json(
                    args.input,
                    output_dir=args.output,
                    base_name=args.name
                )
                print(f"✅ Word: {word_path}")
                if pdf_path:
                    print(f"✅ PDF: {pdf_path}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

    elif args.action == 'validate':
        # Validate JSON
        validator = JSONValidator()
        try:
            with open(args.input, 'r') as f:
                data = json.load(f)

            is_valid, errors = validator.validate_structure(data)
            if is_valid:
                print("✅ JSON is valid!")
                cleaned = validator.clean_data(data)
                print("ℹ️ Data has been cleaned and normalized")
            else:
                print("❌ JSON validation failed:")
                for error in errors:
                    print(f"  - {error}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

    elif args.action == 'backup':
        # Create backup
        backup_mgr = BackupManager()
        try:
            with open(args.input, 'r') as f:
                data = json.load(f)

            backup_path = backup_mgr.create_backup(data, args.name)
            print(f"✅ Backup created: {backup_path}")

            # List all backups
            backups = backup_mgr.list_backups()
            print(f"\n📁 Total backups: {len(backups)}")
            for backup in backups[:5]:  # Show last 5
                print(f"  - {backup['filename']} ({backup['modified']})")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

    elif args.action == 'stats':
        # Generate statistics
        try:
            with open(args.input, 'r') as f:
                data = json.load(f)

            stats = StatisticsGenerator.analyze_resume(data)
            print("\n📊 Resume Statistics:")
            print(f"  Total words: {stats['total_word_count']}")
            print(f"  Bullet points: {stats['bullet_points']}")
            print(f"  Skills: {stats['skills_count']}")

            if 'sections' in stats:
                print("\n  Sections:")
                for section, info in stats['sections'].items():
                    print(f"    {section.capitalize()}:")
                    for key, value in info.items():
                        print(f"      - {key}: {value}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

    elif args.action == 'clean':
        # Clean and format JSON
        validator = JSONValidator()
        try:
            with open(args.input, 'r') as f:
                data = json.load(f)

            cleaned = validator.clean_data(data)

            # Save cleaned version
            output_file = args.input.replace('.json', '_cleaned.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned, f, indent=2)

            print(f"✅ Cleaned JSON saved: {output_file}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

    return True


def main():
    """Main entry point for the application"""
    print("=" * 50)
    print("🚀 Resume Generator - Quick Start")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        print("\n⚠️ Please install missing dependencies first")
        sys.exit(1)

    # Create project structure
    create_project_structure()

    # Create sample JSON if needed
    create_sample_resume_json()

    print("\nChoose an option:")
    print("1. Quick Generate (generate resume with default settings)")
    print("2. Web Interface (launch Streamlit app)")
    print("3. Command Line (advanced options)")
    print("4. Setup Only (exit after setup)")

    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == '1':
        quick_generate()
    elif choice == '2':
        print("\n🌐 Launching web interface...")
        print("Press Ctrl+C to stop the server")
        run_web_interface()
    elif choice == '3':
        print("\n💻 Command-line interface")
        print("Run with -h flag for help: python quickstart.py -h")
        run_cli_interface()
    elif choice == '4':
        print("\n✅ Setup complete! You can now:")
        print("  - Edit resume_data.json with your information")
        print("  - Run 'streamlit run app.py' for web interface")
        print("  - Run 'python quickstart.py' for quick generation")
    else:
        print("\n❌ Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If arguments provided, run CLI mode
        run_cli_interface()
    else:
        # Otherwise, run interactive mode
        main()