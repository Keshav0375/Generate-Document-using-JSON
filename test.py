"""
Testing Module for Resume Generator
Comprehensive tests to ensure all components work correctly
"""

import unittest
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from resume_generator import (
    ResumeGenerator,
    DocumentConfig,
    ResumeFormatter,
    ResumeBuilder
)
from utils import (
    JSONValidator,
    ResumeComparator,
    BackupManager,
    TemplateManager,
    StatisticsGenerator
)


class TestDocumentConfig(unittest.TestCase):
    """Test DocumentConfig class"""

    def test_default_config(self):
        """Test default configuration values"""
        config = DocumentConfig()
        self.assertEqual(config.margin_top, 0.5)
        self.assertEqual(config.margin_bottom, 0.5)
        self.assertEqual(config.font_name, "Calibri")
        self.assertEqual(config.font_size_normal, 11)

    def test_custom_config(self):
        """Test custom configuration"""
        config = DocumentConfig(
            margin_top=1.0,
            font_name="Arial",
            font_size_normal=12
        )
        self.assertEqual(config.margin_top, 1.0)
        self.assertEqual(config.font_name, "Arial")
        self.assertEqual(config.font_size_normal, 12)


class TestJSONValidator(unittest.TestCase):
    """Test JSON validation"""

    def setUp(self):
        self.validator = JSONValidator()
        self.valid_data = {
            'header': {
                'name': 'Test User',
                'email': 'test@example.com'
            },
            'technical_skills': {},
            'education': [],
            'experience': []
        }

    def test_valid_structure(self):
        """Test valid JSON structure"""
        is_valid, errors = self.validator.validate_structure(self.valid_data)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_missing_header(self):
        """Test missing header section"""
        data = self.valid_data.copy()
        del data['header']
        is_valid, errors = self.validator.validate_structure(data)
        self.assertFalse(is_valid)
        self.assertIn("Missing 'header' section", errors)

    def test_invalid_email(self):
        """Test invalid email format"""
        data = self.valid_data.copy()
        data['header']['email'] = 'invalid-email'
        is_valid, errors = self.validator.validate_structure(data)
        self.assertFalse(is_valid)
        self.assertTrue(any('Invalid email format' in e for e in errors))

    def test_email_validation(self):
        """Test email validation function"""
        self.assertTrue(self.validator.validate_email('test@example.com'))
        self.assertTrue(self.validator.validate_email('user.name@domain.co.uk'))
        self.assertFalse(self.validator.validate_email('invalid-email'))
        self.assertFalse(self.validator.validate_email('@example.com'))

    def test_phone_validation(self):
        """Test phone validation function"""
        self.assertTrue(self.validator.validate_phone('123-456-7890'))
        self.assertTrue(self.validator.validate_phone('+1 (234) 567-8900'))
        self.assertTrue(self.validator.validate_phone('1234567890'))
        self.assertFalse(self.validator.validate_phone('123'))
        self.assertFalse(self.validator.validate_phone('abc-def-ghij'))

    def test_url_validation(self):
        """Test URL validation function"""
        self.assertTrue(self.validator.validate_url('https://example.com'))
        self.assertTrue(self.validator.validate_url('http://www.example.com/path'))
        self.assertFalse(self.validator.validate_url('not-a-url'))
        self.assertFalse(self.validator.validate_url('example.com'))

    def test_clean_data(self):
        """Test data cleaning function"""
        data = {
            'header': {
                'name': '  Test User  ',
                'phone': '123 456 7890'
            },
            'experience': [{
                'bullets': [
                    '  Bullet point without period  ',
                    'Bullet point with period.',
                    '',
                    '  '
                ]
            }]
        }

        cleaned = self.validator.clean_data(data)

        # Check trimmed whitespace
        self.assertEqual(cleaned['header']['name'], 'Test User')

        # Check normalized phone
        self.assertEqual(cleaned['header']['phone'], '123-456-7890')

        # Check cleaned bullets
        bullets = cleaned['experience'][0]['bullets']
        self.assertEqual(len(bullets), 2)  # Empty bullets removed
        self.assertTrue(all(b.endswith('.') for b in bullets))


class TestResumeGenerator(unittest.TestCase):
    """Test ResumeGenerator class"""

    def setUp(self):
        self.generator = ResumeGenerator()
        self.temp_dir = tempfile.mkdtemp()
        self.sample_data = {
            'header': {
                'name': 'Test User',
                'email': 'test@example.com',
                'phone': '123-456-7890'
            },
            'technical_skills': {
                'Languages': 'Python, Java',
                'Tools': 'Git, Docker'
            },
            'education': [{
                'degree': 'BS Computer Science',
                'school': 'Test University',
                'location': 'Test City',
                'dates': '2020-2024',
                'gpa': '3.8/4.0',
                'notes': []
            }],
            'experience': [{
                'title': 'Software Engineer',
                'company': 'Test Company',
                'location': 'Test City',
                'dates': '2024-Present',
                'bullets': [
                    'Developed test feature.',
                    'Improved performance.'
                ]
            }],
            'projects': [],
            'competitions': [],
            'certifications': []
        }

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_save_and_load_json(self):
        """Test saving and loading JSON data"""
        json_path = os.path.join(self.temp_dir, 'test.json')

        # Save JSON
        self.generator.save_json(self.sample_data, json_path)
        self.assertTrue(os.path.exists(json_path))

        # Load JSON
        loaded_data = self.generator.load_json(json_path)
        self.assertEqual(loaded_data['header']['name'], 'Test User')

    def test_generate_word(self):
        """Test Word document generation"""
        word_path = os.path.join(self.temp_dir, 'test.docx')
        result = self.generator.generate_word(self.sample_data, word_path)

        self.assertEqual(result, word_path)
        self.assertTrue(os.path.exists(word_path))
        self.assertGreater(os.path.getsize(word_path), 0)

    def test_invalid_json_load(self):
        """Test loading invalid JSON file"""
        # Non-existent file
        with self.assertRaises(FileNotFoundError):
            self.generator.load_json('non_existent.json')

        # Invalid JSON content
        invalid_json_path = os.path.join(self.temp_dir, 'invalid.json')
        with open(invalid_json_path, 'w') as f:
            f.write('{ invalid json }')

        with self.assertRaises(json.JSONDecodeError):
            self.generator.load_json(invalid_json_path)


class TestBackupManager(unittest.TestCase):
    """Test BackupManager class"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.backup_mgr = BackupManager(self.temp_dir)
        self.sample_data = {
            'header': {'name': 'Test User'},
            'experience': []
        }

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_backup(self):
        """Test creating a backup"""
        backup_path = self.backup_mgr.create_backup(self.sample_data, 'test')

        self.assertTrue(os.path.exists(backup_path))
        self.assertIn('test_', os.path.basename(backup_path))

        # Verify backup content
        with open(backup_path, 'r') as f:
            restored = json.load(f)
        self.assertEqual(restored['header']['name'], 'Test User')

    def test_duplicate_backup_detection(self):
        """Test that identical backups are detected"""
        # Create first backup
        backup1 = self.backup_mgr.create_backup(self.sample_data, 'test1')

        # Try to create identical backup
        backup2 = self.backup_mgr.create_backup(self.sample_data, 'test2')

        # Should return the first backup path (deduplication)
        self.assertEqual(backup1, backup2)

    def test_list_backups(self):
        """Test listing backups"""
        # Create multiple backups
        self.backup_mgr.create_backup(self.sample_data, 'backup1')
        self.backup_mgr.create_backup({'different': 'data'}, 'backup2')

        backups = self.backup_mgr.list_backups()
        self.assertEqual(len(backups), 2)
        self.assertTrue(all('filename' in b for b in backups))
        self.assertTrue(all('path' in b for b in backups))

    def test_restore_backup(self):
        """Test restoring from backup"""
        backup_path = self.backup_mgr.create_backup(self.sample_data, 'test')
        restored = self.backup_mgr.restore_backup(backup_path)

        self.assertEqual(restored['header']['name'], 'Test User')


class TestStatisticsGenerator(unittest.TestCase):
    """Test StatisticsGenerator class"""

    def test_word_count(self):
        """Test word counting"""
        text = "This is a test sentence."
        count = StatisticsGenerator.count_words(text)
        self.assertEqual(count, 5)

    def test_analyze_resume(self):
        """Test resume analysis"""
        data = {
            'technical_skills': {
                'Languages': 'Python, Java, C++',
                'Tools': 'Git, Docker'
            },
            'experience': [{
                'bullets': [
                    'First bullet point.',
                    'Second bullet point with more words.'
                ]
            }],
            'projects': [{
                'bullets': ['Project bullet.']
            }],
            'certifications': [
                {'name': 'Cert 1'},
                {'name': 'Cert 2'}
            ]
        }

        stats = StatisticsGenerator.analyze_resume(data)

        self.assertEqual(stats['skills_count'], 5)  # 3 languages + 2 tools
        self.assertEqual(stats['bullet_points'], 3)  # 2 exp + 1 project
        self.assertGreater(stats['total_word_count'], 0)
        self.assertEqual(stats['sections']['certifications']['count'], 2)


class TestTemplateManager(unittest.TestCase):
    """Test TemplateManager class"""

    def test_get_template(self):
        """Test getting a template"""
        template = TemplateManager.get_template('software_engineer')
        self.assertIsNotNone(template)
        self.assertIn('header', template)
        self.assertEqual(template['header']['name'], 'John Doe')

    def test_list_templates(self):
        """Test listing available templates"""
        templates = TemplateManager.list_templates()
        self.assertIn('software_engineer', templates)
        self.assertIn('data_scientist', templates)

    def test_save_as_template(self):
        """Test saving a custom template"""
        temp_dir = tempfile.mkdtemp()
        try:
            data = {'header': {'name': 'Custom Template'}}
            filepath = TemplateManager.save_as_template(
                data, 'custom', temp_dir
            )

            self.assertTrue(os.path.exists(filepath))

            # Verify saved content
            with open(filepath, 'r') as f:
                loaded = json.load(f)
            self.assertEqual(loaded['header']['name'], 'Custom Template')
        finally:
            import shutil
            shutil.rmtree(temp_dir)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config = DocumentConfig()
        self.generator = ResumeGenerator(self.config)

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_end_to_end_generation(self):
        """Test complete resume generation process"""
        # Get template
        template = TemplateManager.get_template('software_engineer')

        # Validate template
        validator = JSONValidator()
        is_valid, errors = validator.validate_structure(template)
        self.assertTrue(is_valid)

        # Clean data
        cleaned = validator.clean_data(template)

        # Generate statistics
        stats = StatisticsGenerator.analyze_resume(cleaned)
        self.assertGreater(stats['skills_count'], 0)

        # Create backup
        backup_mgr = BackupManager(self.temp_dir)
        backup_path = backup_mgr.create_backup(cleaned, 'test')
        self.assertTrue(os.path.exists(backup_path))

        # Generate Word document
        word_path = os.path.join(self.temp_dir, 'test_resume.docx')
        result = self.generator.generate_word(cleaned, word_path)
        self.assertTrue(os.path.exists(result))


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestJSONValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestResumeGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestBackupManager))
    suite.addTests(loader.loadTestsFromTestCase(TestStatisticsGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestTemplateManager))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)