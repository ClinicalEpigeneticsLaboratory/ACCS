import uuid

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django_celery_results.models import TaskResult
from django.core.files.uploadedfile import SimpleUploadedFile

from models_collection.models import ModelInstance
from .models import Sample, Document, Sex


class DocumentModelTest(TestCase):
    def setUp(self):
        self.document = Document.objects.create(
            name="sample-document",
            content="<p>This is a sample document content</p>"
        )

    def test_document_creation(self):
        """Test that a Document instance is created successfully."""
        document = Document.objects.get(name="sample-document")
        self.assertEqual(document.content, "<p>This is a sample document content</p>")
        self.assertIsNotNone(document.creation_date)


class SampleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.task = TaskResult.objects.create(task_id=str(uuid.uuid4()))
        self.model_instance = ModelInstance.objects.create(name="test-model")

        self.sample = Sample.objects.create(
            user=self.user,
            task=self.task,
            model=self.model_instance,
            sample_name="Sample1",
            diagnosis="Diagnosis1",
            age=30,
            sex=Sex.Male,
        )

    def test_sample_creation(self):
        """Test that a Sample instance is created successfully."""
        sample = Sample.objects.get(sample_name="Sample1")
        self.assertEqual(sample.diagnosis, "Diagnosis1")
        self.assertEqual(sample.age, 30)
        self.assertEqual(sample.sex, Sex.Male)
        self.assertEqual(str(sample), "Sample1")
        self.assertIsNotNone(sample.creation_date)

    def test_sample_path_method(self):
        """Test the path method to ensure it generates correct paths for files."""
        file_name = "test_file_Grn.idat"
        expected_path = f"tasks/{self.sample.id}/idats/{file_name}"
        self.assertEqual(self.sample.path(file_name), expected_path)

    def test_grn_idat_file_validation(self):
        """Test that only files with the correct grn idat naming convention can be uploaded."""
        valid_file = SimpleUploadedFile("test_Grn.idat", b"dummy content")
        self.sample.grn_idat = valid_file
        try:
            self.sample.full_clean()  # Run validations
        except ValidationError:
            self.fail("Sample should accept valid grn idat file names.")

        # Testing with an invalid file name
        invalid_file = SimpleUploadedFile("test.txt", b"dummy content")
        self.sample.grn_idat = invalid_file
        with self.assertRaises(ValidationError):
            self.sample.full_clean()

    def test_red_idat_file_validation(self):
        """Test that only files with the correct red idat naming convention can be uploaded."""
        valid_file = SimpleUploadedFile("test_Red.idat", b"dummy content")
        self.sample.red_idat = valid_file
        try:
            self.sample.full_clean()  # Run validations
        except ValidationError:
            self.fail("Sample should accept valid red idat file names.")

        # Testing with an invalid file name
        invalid_file = SimpleUploadedFile("test_invalid.txt", b"dummy content")
        self.sample.red_idat = invalid_file
        with self.assertRaises(ValidationError):
            self.sample.full_clean()

    def test_sample_sex_choice_validation(self):
        """Test that only valid choices for sex can be saved."""
        self.sample.sex = Sex.Male  # Valid choice
        self.sample.full_clean()  # Should not raise an error

        self.sample.sex = "InvalidChoice"  # Invalid choice
        with self.assertRaises(ValidationError):
            self.sample.full_clean()

    def test_sample_foreign_key_relationships(self):
        """Test that the foreign key relationships are set up correctly."""
        sample = Sample.objects.get(id=self.sample.id)
        self.assertEqual(sample.user, self.user)
        self.assertEqual(sample.task, self.task)
        self.assertEqual(sample.model, self.model_instance)
