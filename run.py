#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Command Line Interface for Resume Generator
'''

import argparse
import json
import os
import sys
from pathlib import Path
from resume_generator import ResumeGenerator, DocumentConfig


def validate_json_file(filepath):
    '''Validate JSON file exists and is valid'''
    if not os.path.exists(filepath):
        raise argparse.ArgumentTypeError(f"File not found: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            json.load(f)
    except json.JSONDecodeError:
        raise argparse.ArgumentTypeError(f"Invalid JSON file: {filepath}")

    return filepath


def main():
    parser = argparse.ArgumentParser(
        description='Generate resume from JSON data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python run.py resume_data.json
  python run.py resume_data.json -o ./output
  python run.py resume_data.json -n john_doe_resume
  python run.py resume_data.json --word-only
        '''
    )

    parser.add_argument(
        'json_file',
        type=validate_json_file,
        help='Path to JSON file containing resume data'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='./output',
        help='Output directory (default: ./output)'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        default='resume',
        help='Base name for output files (default: resume)'
    )

    parser.add_argument(
        '--word-only',
        action='store_true',
        help='Generate only Word document (skip PDF)'
    )

    parser.add_argument(
        '--margin-top',
        type=float,
        default=0.5,
        help='Top margin in inches (default: 0.5)'
    )

    parser.add_argument(
        '--margin-bottom',
        type=float,
        default=0.5,
        help='Bottom margin in inches (default: 0.5)'
    )

    parser.add_argument(
        '--margin-left',
        type=float,
        default=0.5,
        help='Left margin in inches (default: 0.5)'
    )

    parser.add_argument(
        '--margin-right',
        type=float,
        default=0.5,
        help='Right margin in inches (default: 0.5)'
    )

    parser.add_argument(
        '--font',
        type=str,
        default='Calibri',
        choices=['Calibri', 'Arial', 'Times New Roman', 'Georgia'],
        help='Font family (default: Calibri)'
    )

    parser.add_argument(
        '--font-size',
        type=int,
        default=11,
        help='Base font size (default: 11)'
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

    # Create generator
    generator = ResumeGenerator(config)

    try:
        print(f"Generating resume from: {args.json_file}")
        print(f"Output directory: {args.output}")
        print("-" * 40)

        # Create output directory if it doesn't exist
        Path(args.output).mkdir(parents=True, exist_ok=True)

        if args.word_only:
            # Generate only Word document
            resume_data = generator.load_json(args.json_file)
            word_path = os.path.join(args.output, f"{args.name}.docx")
            generator.generate_word(resume_data, word_path)
            print(f"Word document: {word_path}")
        else:
            # Generate both Word and PDF
            word_path, pdf_path = generator.generate_from_json(
                args.json_file,
                output_dir=args.output,
                base_name=args.name
            )
            print(f"Word document: {word_path}")
            if pdf_path:
                print(f"PDF document: {pdf_path}")
            else:
                print("PDF generation failed (docx2pdf not available)")

        print("-" * 40)
        print("Resume generation complete!")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
