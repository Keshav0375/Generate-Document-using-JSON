"""
Utility Functions for Resume Generator
Helper functions for JSON manipulation, validation, and file operations
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging
from difflib import SequenceMatcher
import hashlib

logger = logging.getLogger(__name__)


class JSONValidator:
    """Validate and clean resume JSON data"""

    REQUIRED_FIELDS = {
        'header': ['name', 'email'],
        'technical_skills': [],
        'education': ['degree', 'school'],
        'experience': ['title', 'company']
    }

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)\.]+', '', phone)
        # Check if it's a valid phone number (10-15 digits)
        return re.match(r'^\+?\d{10,15}$', cleaned) is not None

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return re.match(pattern, url) is not None

    @classmethod
    def validate_structure(cls, data: Dict) -> Tuple[bool, List[str]]:
        """Validate JSON structure and return errors"""
        errors = []

        # Check header
        if 'header' not in data:
            errors.append("Missing 'header' section")
        else:
            header = data['header']
            for field in cls.REQUIRED_FIELDS['header']:
                if not header.get(field):
                    errors.append(f"Missing required field: header.{field}")

            # Validate email if present
            if header.get('email') and not cls.validate_email(header['email']):
                errors.append(f"Invalid email format: {header['email']}")

            # Validate phone if present
            if header.get('phone') and not cls.validate_phone(header['phone']):
                errors.append(f"Invalid phone format: {header['phone']}")

            # Validate URLs if present
            for url_field in ['linkedin', 'portfolio', 'github']:
                if header.get(url_field) and not cls.validate_url(header[url_field]):
                    errors.append(f"Invalid URL format: {url_field}")

        # Check other sections exist
        for section in ['technical_skills', 'education', 'experience']:
            if section not in data:
                errors.append(f"Missing '{section}' section")

        return len(errors) == 0, errors

    @staticmethod
    def clean_data(data: Dict) -> Dict:
        """Clean and normalize resume data"""
        cleaned = data.copy()

        # Clean header
        if 'header' in cleaned:
            header = cleaned['header']
            # Trim whitespace
            for key in header:
                if isinstance(header[key], str):
                    header[key] = header[key].strip()

            # Normalize phone number
            if header.get('phone'):
                phone = re.sub(r'[\s\-\(\)\.]+', '-', header['phone'])
                header['phone'] = phone

        # Clean experience and projects bullets
        for section in ['experience', 'projects']:
            if section in cleaned:
                for item in cleaned[section]:
                    if 'bullets' in item:
                        # Remove empty bullets and trim
                        item['bullets'] = [
                            b.strip() for b in item['bullets']
                            if b and b.strip()
                        ]
                        # Ensure bullets end with period
                        item['bullets'] = [
                            b if b.endswith('.') else b + '.'
                            for b in item['bullets']
                        ]

        # Clean education notes
        if 'education' in cleaned:
            for edu in cleaned['education']:
                if 'notes' in edu:
                    edu['notes'] = [
                        n.strip() for n in edu['notes']
                        if n and n.strip()
                    ]

        return cleaned


class ResumeComparator:
    """Compare two resume versions and highlight differences"""

    @staticmethod
    def compare_json(old_data: Dict, new_data: Dict) -> Dict:
        """Compare two resume JSONs and return differences"""
        differences = {
            'added': {},
            'removed': {},
            'modified': {}
        }

        all_keys = set(old_data.keys()) | set(new_data.keys())

        for key in all_keys:
            if key not in old_data:
                differences['added'][key] = new_data[key]
            elif key not in new_data:
                differences['removed'][key] = old_data[key]
            elif old_data[key] != new_data[key]:
                differences['modified'][key] = {
                    'old': old_data[key],
                    'new': new_data[key]
                }

        return differences

    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts"""
        return SequenceMatcher(None, text1, text2).ratio()


class BackupManager:
    """Manage resume backups and versions"""

    def __init__(self, backup_dir: str = "./backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self, data: Dict, name: str = None) -> str:
        """Create a backup of resume data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate hash for deduplication
        data_str = json.dumps(data, sort_keys=True)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()[:8]

        # Create filename
        if name:
            filename = f"{name}_{timestamp}_{data_hash}.json"
        else:
            filename = f"backup_{timestamp}_{data_hash}.json"

        filepath = self.backup_dir / filename

        # Check if identical backup exists
        for existing in self.backup_dir.glob(f"*_{data_hash}.json"):
            logger.info(f"Identical backup already exists: {existing}")
            return str(existing)

        # Save backup
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Backup created: {filepath}")
        return str(filepath)

    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []

        for filepath in sorted(self.backup_dir.glob("*.json"), reverse=True):
            stat = filepath.stat()
            backups.append({
                'filename': filepath.name,
                'path': str(filepath),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'hash': filepath.stem.split('_')[-1] if '_' in filepath.stem else None
            })

        return backups

    def restore_backup(self, backup_path: str) -> Dict:
        """Restore resume data from backup"""
        with open(backup_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def cleanup_old_backups(self, keep_count: int = 10):
        """Remove old backups, keeping the most recent ones"""
        backups = sorted(self.backup_dir.glob("*.json"),
                         key=lambda p: p.stat().st_mtime,
                         reverse=True)

        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                backup.unlink()
                logger.info(f"Deleted old backup: {backup}")


class TemplateManager:
    """Manage resume templates"""

    TEMPLATES = {
        'software_engineer': {
            'header': {
                'name': 'John Doe',
                'phone': '555-123-4567',
                'email': 'john.doe@email.com',
                'location': 'San Francisco, CA',
                'linkedin': 'https://linkedin.com/in/johndoe',
                'github': 'https://github.com/johndoe'
            },
            'technical_skills': {
                'Languages': 'Python, JavaScript, Java, C++',
                'Frameworks': 'React, Django, Spring Boot, Express.js',
                'Databases': 'PostgreSQL, MongoDB, Redis',
                'Tools': 'Git, Docker, Kubernetes, AWS'
            },
            'education': [
                {
                    'degree': 'Bachelor of Science in Computer Science',
                    'school': 'University of California, Berkeley',
                    'location': 'Berkeley, CA',
                    'dates': 'Sep 2018 - May 2022',
                    'gpa': 'GPA: 3.8/4.0',
                    'notes': []
                }
            ],
            'experience': [
                {
                    'title': 'Software Engineer',
                    'company': 'Tech Company',
                    'location': 'San Francisco, CA',
                    'dates': 'Jun 2022 - Present',
                    'bullets': [
                        'Developed and maintained microservices handling 1M+ requests daily.',
                        'Improved API response time by 40% through optimization.',
                        'Led migration from monolithic to microservices architecture.'
                    ]
                }
            ],
            'projects': [],
            'competitions': [],
            'certifications': []
        },
        'data_scientist': {
            'header': {
                'name': 'Jane Smith',
                'phone': '555-987-6543',
                'email': 'jane.smith@email.com',
                'location': 'New York, NY',
                'linkedin': 'https://linkedin.com/in/janesmith',
                'github': 'https://github.com/janesmith'
            },
            'technical_skills': {
                'Languages': 'Python, R, SQL, Scala',
                'ML/DL': 'TensorFlow, PyTorch, Scikit-learn, XGBoost',
                'Big Data': 'Spark, Hadoop, Hive, Kafka',
                'Tools': 'Tableau, PowerBI, Jupyter, Git'
            },
            'education': [
                {
                    'degree': 'Master of Science in Data Science',
                    'school': 'Columbia University',
                    'location': 'New York, NY',
                    'dates': 'Sep 2020 - May 2022',
                    'gpa': 'GPA: 3.9/4.0',
                    'notes': []
                }
            ],
            'experience': [
                {
                    'title': 'Data Scientist',
                    'company': 'Analytics Corp',
                    'location': 'New York, NY',
                    'dates': 'Jun 2022 - Present',
                    'bullets': [
                        'Built ML models improving customer retention by 25%.',
                        'Developed real-time recommendation system serving 10M+ users.',
                        'Created automated reporting dashboards saving 20 hours weekly.'
                    ]
                }
            ],
            'projects': [],
            'competitions': [],
            'certifications': []
        }
    }

    @classmethod
    def get_template(cls, template_name: str) -> Optional[Dict]:
        """Get a template by name"""
        return cls.TEMPLATES.get(template_name)

    @classmethod
    def list_templates(cls) -> List[str]:
        """List available template names"""
        return list(cls.TEMPLATES.keys())

    @classmethod
    def save_as_template(cls, data: Dict, template_name: str,
                         templates_dir: str = "./templates") -> str:
        """Save current resume as a template"""
        templates_path = Path(templates_dir)
        templates_path.mkdir(exist_ok=True)

        filepath = templates_path / f"{template_name}.json"

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Template saved: {filepath}")
        return str(filepath)


class StatisticsGenerator:
    """Generate statistics about resume content"""

    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text"""
        return len(text.split())

    @staticmethod
    def analyze_resume(data: Dict) -> Dict:
        """Generate statistics about resume"""
        stats = {
            'total_word_count': 0,
            'sections': {},
            'bullet_points': 0,
            'skills_count': 0,
            'experience_years': 0
        }

        # Count skills
        if 'technical_skills' in data:
            for category, skills in data['technical_skills'].items():
                skills_list = [s.strip() for s in skills.split(',')]
                stats['skills_count'] += len(skills_list)

        # Count experience bullets and words
        if 'experience' in data:
            stats['sections']['experience'] = {
                'count': len(data['experience']),
                'bullets': 0,
                'words': 0
            }
            for exp in data['experience']:
                bullets = exp.get('bullets', [])
                stats['sections']['experience']['bullets'] += len(bullets)
                stats['bullet_points'] += len(bullets)

                for bullet in bullets:
                    word_count = StatisticsGenerator.count_words(bullet)
                    stats['sections']['experience']['words'] += word_count
                    stats['total_word_count'] += word_count

        # Count projects
        if 'projects' in data:
            stats['sections']['projects'] = {
                'count': len(data['projects']),
                'bullets': 0,
                'words': 0
            }
            for proj in data['projects']:
                bullets = proj.get('bullets', [])
                stats['sections']['projects']['bullets'] += len(bullets)
                stats['bullet_points'] += len(bullets)

                for bullet in bullets:
                    word_count = StatisticsGenerator.count_words(bullet)
                    stats['sections']['projects']['words'] += word_count
                    stats['total_word_count'] += word_count

        # Count education
        if 'education' in data:
            stats['sections']['education'] = {
                'count': len(data['education'])
            }

        # Count certifications
        if 'certifications' in data:
            stats['sections']['certifications'] = {
                'count': len(data['certifications'])
            }

        return stats


# Export functions for easy import
__all__ = [
    'JSONValidator',
    'ResumeComparator',
    'BackupManager',
    'TemplateManager',
    'StatisticsGenerator'
]

# Example usage and testing
if __name__ == "__main__":
    # Test JSON validation
    sample_data = {
        'header': {
            'name': 'Test User',
            'email': 'test@example.com',
            'phone': '123-456-7890'
        },
        'technical_skills': {},
        'education': [],
        'experience': []
    }

    validator = JSONValidator()
    is_valid, errors = validator.validate_structure(sample_data)
    print(f"Validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
    if errors:
        print("Errors:", errors)

    # Test backup manager
    backup_mgr = BackupManager()
    backup_path = backup_mgr.create_backup(sample_data, "test")
    print(f"Backup created: {backup_path}")

    # Test statistics
    stats = StatisticsGenerator.analyze_resume(sample_data)
    print("Resume statistics:", json.dumps(stats, indent=2))