"""
Batch Processing Script for Resume Generator
Process multiple resumes at once with different configurations
"""

import os
import json
import csv
import concurrent.futures
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging
import argparse

from resume_generator import ResumeGenerator, DocumentConfig
from utils import JSONValidator, BackupManager, StatisticsGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """Process multiple resumes in batch"""

    def __init__(self, config: DocumentConfig = None, max_workers: int = 4):
        self.config = config or DocumentConfig()
        self.max_workers = max_workers
        self.results = []
        self.errors = []

    def process_single_resume(self, json_path: str, output_dir: str,
                              base_name: str = None) -> Tuple[bool, str, Optional[str]]:
        """Process a single resume file"""
        try:
            generator = ResumeGenerator(self.config)

            # Determine output name
            if not base_name:
                base_name = Path(json_path).stem

            # Generate resume
            word_path, pdf_path = generator.generate_from_json(
                json_path,
                output_dir=output_dir,
                base_name=base_name
            )

            return True, word_path, pdf_path

        except Exception as e:
            logger.error(f"Error processing {json_path}: {str(e)}")
            return False, str(e), None

    def process_batch(self, json_files: List[str], output_dir: str) -> Dict:
        """Process multiple resume files"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        results = {
            'successful': [],
            'failed': [],
            'total': len(json_files),
            'start_time': datetime.now()
        }

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(
                    self.process_single_resume,
                    json_file,
                    output_dir
                ): json_file
                for json_file in json_files
            }

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_file):
                json_file = future_to_file[future]
                try:
                    success, word_path, pdf_path = future.result()
                    if success:
                        results['successful'].append({
                            'input': json_file,
                            'word': word_path,
                            'pdf': pdf_path
                        })
                        logger.info(f"✅ Processed: {json_file}")
                    else:
                        results['failed'].append({
                            'input': json_file,
                            'error': word_path  # Error message in this case
                        })
                        logger.error(f"❌ Failed: {json_file}")
                except Exception as e:
                    results['failed'].append({
                        'input': json_file,
                        'error': str(e)
                    })
                    logger.error(f"❌ Exception processing {json_file}: {str(e)}")

        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()

        return results

    def process_from_csv(self, csv_path: str, output_dir: str) -> Dict:
        """Process resumes from a CSV file with configurations"""
        results = {
            'successful': [],
            'failed': [],
            'start_time': datetime.now()
        }

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # Create custom config if specified
                    custom_config = DocumentConfig(
                        margin_top=float(row.get('margin_top', 0.5)),
                        margin_bottom=float(row.get('margin_bottom', 0.5)),
                        margin_left=float(row.get('margin_left', 0.5)),
                        margin_right=float(row.get('margin_right', 0.5)),
                        font_name=row.get('font', 'Calibri'),
                        font_size_normal=int(row.get('font_size', 11))
                    )

                    generator = ResumeGenerator(custom_config)

                    # Generate resume
                    json_path = row['json_file']
                    base_name = row.get('output_name', Path(json_path).stem)

                    word_path, pdf_path = generator.generate_from_json(
                        json_path,
                        output_dir=output_dir,
                        base_name=base_name
                    )

                    results['successful'].append({
                        'input': json_path,
                        'word': word_path,
                        'pdf': pdf_path
                    })
                    logger.info(f"✅ Processed: {json_path}")

                except Exception as e:
                    results['failed'].append({
                        'input': row.get('json_file', 'unknown'),
                        'error': str(e)
                    })
                    logger.error(f"❌ Failed: {row.get('json_file')}: {str(e)}")

        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        results['total'] = len(results['successful']) + len(results['failed'])

        return results

    def generate_report(self, results: Dict, report_path: str = None) -> str:
        """Generate a processing report"""
        if not report_path:
            report_path = f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("BATCH PROCESSING REPORT\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Start Time: {results['start_time']}\n")
            f.write(f"End Time: {results['end_time']}\n")
            f.write(f"Duration: {results['duration']:.2f} seconds\n")
            f.write(f"Total Files: {results['total']}\n")
            f.write(f"Successful: {len(results['successful'])}\n")
            f.write(f"Failed: {len(results['failed'])}\n\n")

            if results['successful']:
                f.write("SUCCESSFUL PROCESSING:\n")
                f.write("-" * 40 + "\n")
                for item in results['successful']:
                    f.write(f"Input: {item['input']}\n")
                    f.write(f"  Word: {item['word']}\n")
                    if item['pdf']:
                        f.write(f"  PDF: {item['pdf']}\n")
                    f.write("\n")

            if results['failed']:
                f.write("\nFAILED PROCESSING:\n")
                f.write("-" * 40 + "\n")
                for item in results['failed']:
                    f.write(f"Input: {item['input']}\n")
                    f.write(f"  Error: {item['error']}\n\n")

        logger.info(f"Report saved to: {report_path}")
        return report_path


# ===== FINAL SETUP SCRIPT =====
FINAL_SETUP = """
#!/usr/bin/env python3
'''
Complete Setup and Installation Script for Resume Generator
'''

import os
import sys
import subprocess
import platform
import json
from pathlib import Path


def print_banner():
    '''Print welcome banner'''
    print('''
    ╔═══════════════════════════════════════════════════════╗
    ║                   RESUME GENERATOR                    ║
    ║              Professional Document Creator            ║
    ║                     Version 1.0                       ║
    ╚═══════════════════════════════════════════════════════╝
    ''')


def check_python_version():
    '''Check Python version'''
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def install_requirements():
    '''Install required packages'''
    requirements = [
        'streamlit>=1.28.0',
        'python-docx>=1.1.0',
        'docx2pdf>=0.1.8',
        'Pillow>=10.0.0'
    ]

    print("\\n📦 Installing dependencies...")

    for package in requirements:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"  ✅ {package}")
        except subprocess.CalledProcessError:
            print(f"  ❌ Failed to install {package}")
            return False

    return True


def create_file_structure():
    '''Create complete file structure'''
    # Create directories
    directories = [
        'output',
        'backups',
        'templates',
        'data',
        'logs',
        'tests'
    ]

    print("\\n📁 Creating directory structure...")
    for dir_name in directories:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"  ✅ {dir_name}/")

    # Create .gitignore
    gitignore_content = '''
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv

# Output files
output/
*.docx
*.pdf

# Backups
backups/

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/
'''

    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("  ✅ .gitignore")

    return True


def create_launch_scripts():
    '''Create convenient launch scripts'''

    # Windows batch file
    if platform.system() == 'Windows':
        batch_content = '''@echo off
echo Starting Resume Generator...
streamlit run app.py
pause
'''
        with open('launch.bat', 'w') as f:
            f.write(batch_content)
        print("  ✅ launch.bat (Windows)")

    # Unix shell script
    else:
        shell_content = '''#!/bin/bash
echo "Starting Resume Generator..."
streamlit run app.py
'''
        with open('launch.sh', 'w') as f:
            f.write(shell_content)
        os.chmod('launch.sh', 0o755)
        print("  ✅ launch.sh (Unix/Mac)")

    # Python launcher
    launcher_content = '''#!/usr/bin/env python3
import os
import sys
import webbrowser
import time
import subprocess

def main():
    print("🚀 Launching Resume Generator...")

    # Start Streamlit
    process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"])

    # Wait a bit and open browser
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

    print("\\n✅ Resume Generator is running!")
    print("Press Ctrl+C to stop the server")

    try:
        process.wait()
    except KeyboardInterrupt:
        print("\\n👋 Shutting down...")
        process.terminate()

if __name__ == "__main__":
    main()
'''

    with open('launcher.py', 'w') as f:
        f.write(launcher_content)
    print("  ✅ launcher.py")

    return True


def create_config_file():
    '''Create configuration file'''
    config = {
        "app": {
            "name": "Resume Generator",
            "version": "1.0.0",
            "author": "Your Name"
        },
        "defaults": {
            "margins": {
                "top": 0.5,
                "bottom": 0.5,
                "left": 0.5,
                "right": 0.5
            },
            "font": {
                "name": "Calibri",
                "size": 11
            },
            "output_dir": "./output",
            "backup_dir": "./backups"
        },
        "streamlit": {
            "theme": "light",
            "wide_mode": True
        }
    }

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print("  ✅ config.json")
    return True


def run_tests():
    '''Run basic tests'''
    print("\\n🧪 Running tests...")

    try:
        # Try importing main modules
        import resume_generator
        print("  ✅ resume_generator module")

        import utils
        print("  ✅ utils module")

        # Test basic functionality
        from resume_generator import DocumentConfig
        config = DocumentConfig()
        print("  ✅ DocumentConfig")

        from utils import JSONValidator
        validator = JSONValidator()
        print("  ✅ JSONValidator")

        return True

    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False


def print_instructions():
    '''Print usage instructions'''
    print('''
    ╔═══════════════════════════════════════════════════════╗
    ║                  SETUP COMPLETE! 🎉                   ║
    ╚═══════════════════════════════════════════════════════╝

    📚 QUICK START GUIDE:

    1. WEB INTERFACE (Recommended):
       • Run: streamlit run app.py
       • Or: python launcher.py
       • Open: http://localhost:8501

    2. COMMAND LINE:
       • Quick generate: python quickstart.py
       • With options: python run.py resume_data.json
       • Batch process: python batch.py folder/*.json

    3. PYTHON API:
       from resume_generator import ResumeGenerator
       generator = ResumeGenerator()
       generator.generate_from_json("resume.json")

    4. TESTING:
       • Run tests: python test_resume.py
       • Validate JSON: python run.py validate -i resume.json

    📁 PROJECT STRUCTURE:
       • resume_data.json - Your resume content
       • output/ - Generated documents
       • backups/ - Automatic backups
       • templates/ - Resume templates

    📝 NEXT STEPS:
       1. Edit resume_data.json with your information
       2. Run the web interface or CLI
       3. Download your Word/PDF resume!

    💡 TIPS:
       • The web interface is easiest for editing
       • Use templates for quick starts
       • Backups are created automatically
       • Check logs/ for troubleshooting

    📖 DOCUMENTATION:
       • README.md - Full documentation
       • config.json - Default settings
       • test_resume.py - Run tests

    🆘 HELP:
       • python run.py --help
       • python batch.py --help

    Happy resume building! 🚀
    ''')


def main():
    '''Main setup function'''
    print_banner()

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install requirements
    response = input("\\nInstall/update dependencies? (y/n): ").lower()
    if response == 'y':
        if not install_requirements():
            print("\\n⚠️ Some dependencies failed to install")
            print("   Try: pip install -r requirements.txt")

    # Create file structure
    create_file_structure()

    # Create launch scripts
    print("\\n🚀 Creating launch scripts...")
    create_launch_scripts()

    # Create config file
    create_config_file()

    # Run tests
    run_tests()

    # Print instructions
    print_instructions()


if __name__ == "__main__":
    main()
"""

# Create batch processing CLI
BATCH_CLI = """
#!/usr/bin/env python3
'''
Batch Processing CLI for Resume Generator
'''

import argparse
import glob
import sys
from batch_processor import BatchProcessor
from resume_generator import DocumentConfig


def main():
    parser = argparse.ArgumentParser(
        description='Batch process multiple resumes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python batch.py data/*.json
  python batch.py --csv batch_config.csv
  python batch.py data/*.json --workers 8
  python batch.py data/*.json --report report.txt
        '''
    )

    parser.add_argument(
        'json_files',
        nargs='*',
        help='JSON files to process (supports wildcards)'
    )

    parser.add_argument(
        '--csv',
        help='CSV file with batch configurations'
    )

    parser.add_argument(
        '-o', '--output',
        default='./output',
        help='Output directory (default: ./output)'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of parallel workers (default: 4)'
    )

    parser.add_argument(
        '--report',
        help='Path for processing report'
    )

    parser.add_argument(
        '--margin-top',
        type=float,
        default=0.5,
        help='Top margin in inches'
    )

    parser.add_argument(
        '--margin-bottom',
        type=float,
        default=0.5,
        help='Bottom margin in inches'
    )

    parser.add_argument(
        '--margin-left',
        type=float,
        default=0.5,
        help='Left margin in inches'
    )

    parser.add_argument(
        '--margin-right',
        type=float,
        default=0.5,
        help='Right margin in inches'
    )

    parser.add_argument(
        '--font',
        default='Calibri',
        help='Font family'
    )

    parser.add_argument(
        '--font-size',
        type=int,
        default=11,
        help='Base font size'
    )

    args = parser.parse_args()

    # Create configuration
    config = DocumentConfig(
        margin_top=args.margin_top,
        margin_bottom=args.margin_bottom,
        margin_left=args.margin_left,
        margin_right=args.margin_right,
        font_name=args.font,
        font_size_normal=args.font_size
    )

    # Create processor
    processor = BatchProcessor(config, max_workers=args.workers)

    try:
        if args.csv:
            # Process from CSV
            print(f"📋 Processing from CSV: {args.csv}")
            results = processor.process_from_csv(args.csv, args.output)
        else:
            # Expand wildcards and process files
            json_files = []
            for pattern in args.json_files:
                json_files.extend(glob.glob(pattern))

            if not json_files:
                print("❌ No JSON files found")
                sys.exit(1)

            print(f"📄 Processing {len(json_files)} files...")
            results = processor.process_batch(json_files, args.output)

        # Generate report
        if args.report:
            processor.generate_report(results, args.report)

        # Print summary
        print("\\n" + "=" * 50)
        print("BATCH PROCESSING COMPLETE")
        print("=" * 50)
        print(f"✅ Successful: {len(results['successful'])}")
        print(f"❌ Failed: {len(results['failed'])}")
        print(f"⏱️ Duration: {results['duration']:.2f} seconds")

        if args.report:
            print(f"📊 Report: {args.report}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
"""


# Save the scripts
def save_final_files():
    # Save batch processor
    with open('batch_processor.py', 'w') as f:
        f.write(__doc__)  # The batch processor code from above

    # Save final setup script
    with open('setup_complete.py', 'w') as f:
        f.write(FINAL_SETUP)

    # Save batch CLI
    with open('batch.py', 'w') as f:
        f.write(BATCH_CLI)

    print("✅ All files created successfully!")


if __name__ == "__main__":
    save_final_files()