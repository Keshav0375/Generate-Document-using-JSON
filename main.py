"""
Updated Main Script with Template Support
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

from enhanced_generator import TemplateResumeGenerator
from template_analyzer import TemplateAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    required = ['docx', 'docx2pdf', 'streamlit']
    missing = []

    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)

    if missing:
        print(f"⚠️ Missing: {', '.join(missing)}")
        print(f"Run: pip install {' '.join(missing)}")
        return False
    return True

def setup_directories():
    """Create project directories"""
    dirs = ['output', 'data', 'templates']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
    print("✅ Directories created")

def quick_generate_with_template():
    """Generate resume using template if available"""
    try:
        generator = TemplateResumeGenerator()

        # Look for template in data/ directory
        template_path = None
        for ext in ['.docx', '.doc']:
            for name in ['template', 'sample', 'example']:
                path = f"data/{name}{ext}"
                if os.path.exists(path):
                    template_path = path
                    break
            if template_path:
                break

        if template_path:
            print(f"📋 Using template: {template_path}")
            word_file, pdf_file = generator.generate_with_template(
                json_path="resume_data.json",
                template_path=template_path,
                output_dir="output"
            )
        else:
            print("📋 No template found, using default formatting")
            word_file, pdf_file = generator.generate_with_template(
                json_path="resume_data.json",
                output_dir="output"
            )

        print(f"✅ Word: {word_file}")
        if pdf_file:
            print(f"✅ PDF: {pdf_file}")
        else:
            print("⚠️ PDF generation failed")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

def analyze_template():
    """Analyze template document"""
    template_files = []
    data_dir = Path("data")

    if data_dir.exists():
        template_files = list(data_dir.glob("*.docx")) + list(data_dir.glob("*.doc"))

    if not template_files:
        print("❌ No template files found in data/ directory")
        return

    print("📋 Found templates:")
    for i, file in enumerate(template_files):
        print(f"  {i+1}. {file.name}")

    choice = input(f"Choose template (1-{len(template_files)}): ").strip()

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(template_files):
            template_path = template_files[idx]

            analyzer = TemplateAnalyzer()
            stats = analyzer.analyze_document(str(template_path))

            output_file = f"analysis_{template_path.stem}.json"
            analyzer.save_analysis(stats, output_file)

            print(f"✅ Analysis saved to {output_file}")

            # Show summary
            print("\n📊 Template Summary:")
            print(f"  Paragraphs: {stats['document_info']['total_paragraphs']}")
            print(f"  Styles: {len(stats['styles'])}")

            patterns = stats.get('formatting_patterns', {})
            if patterns.get('common_fonts'):
                fonts = patterns['common_fonts']
                main_font = max(fonts, key=fonts.get)
                print(f"  Main font: {main_font}")

        else:
            print("❌ Invalid choice")
    except (ValueError, IndexError):
        print("❌ Invalid choice")

def run_cli():
    """Enhanced CLI with template support"""
    parser = argparse.ArgumentParser(description='Enhanced Resume Generator')

    parser.add_argument('action', choices=['generate', 'analyze', 'help'],
                       help='Action to perform')
    parser.add_argument('-j', '--json', default='resume_data.json',
                       help='Resume JSON file')
    parser.add_argument('-t', '--template', help='Template Word file')
    parser.add_argument('-o', '--output', default='output',
                       help='Output directory')

    args = parser.parse_args()

    if args.action == 'generate':
        try:
            generator = TemplateResumeGenerator()
            word_file, pdf_file = generator.generate_with_template(
                json_path=args.json,
                template_path=args.template,
                output_dir=args.output
            )
            print(f"✅ Generated: {word_file}")
            if pdf_file:
                print(f"✅ PDF: {pdf_file}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    elif args.action == 'analyze':
        if not args.template:
            print("❌ Template file required for analysis")
            return

        try:
            analyzer = TemplateAnalyzer()
            stats = analyzer.analyze_document(args.template)

            output_file = f"analysis_{Path(args.template).stem}.json"
            analyzer.save_analysis(stats, output_file)
            print(f"✅ Analysis saved to {output_file}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

    elif args.action == 'help':
        print("""
Enhanced Resume Generator Commands:

generate    Generate resume from JSON
  -j JSON_FILE     Resume data file (default: resume_data.json)
  -t TEMPLATE      Template Word file (optional)
  -o OUTPUT_DIR    Output directory (default: output)

analyze     Analyze template document
  -t TEMPLATE      Template Word file (required)

Examples:
  python main.py generate -j resume_data.json -t data/template.docx
  python main.py analyze -t data/template.docx
        """)

def run_web_interface():
    """Launch Streamlit with template support"""
    try:
        os.system("streamlit run app.py")
    except:
        print("❌ Streamlit not available")

def main():
    """Main entry point with template support"""
    print("=" * 50)
    print("🚀 Enhanced Resume Generator with Template Support")
    print("=" * 50)

    if not check_dependencies():
        print("\n⚠️ Install missing dependencies first")
        sys.exit(1)

    setup_directories()

    # Create sample data if needed
    if not os.path.exists('resume_data.json'):
        print("📝 Creating sample resume_data.json...")
        # Use the existing resume_data.json content
        print("✅ Please add your resume_data.json file")

    print("\nOptions:")
    print("1. Quick Generate (with template if available)")
    print("2. Analyze Template")
    print("3. Web Interface")
    print("4. Command Line Help")
    print("5. Exit")

    choice = input("\nChoose (1-5): ").strip()

    if choice == '1':
        quick_generate_with_template()
    elif choice == '2':
        analyze_template()
    elif choice == '3':
        print("🌐 Launching web interface...")
        run_web_interface()
    elif choice == '4':
        run_cli()
    elif choice == '5':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_cli()
    else:
        main()