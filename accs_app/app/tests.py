from os.path import join, exists
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.conf import settings

from .models import Sample, User, Sex


class SampleModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="password123")
        self.sample_data = {
            "user": self.user,
            "sample_name": "TestSample",
            "diagnosis": "Healthy",
            "age": 30,
            "sex": Sex.Male,
        }

    def test_sample_creation(self):
        sample = Sample.objects.create(**self.sample_data)
        self.assertEqual(sample.sample_name, "TestSample")
        self.assertEqual(sample.diagnosis, "Healthy")
        self.assertEqual(sample.age, 30)
        self.assertEqual(sample.sex, Sex.Male)

    def test_file_field_validators(self):
        grn_file = SimpleUploadedFile("sample_Grn.idat", b"dummy content")
        red_file = SimpleUploadedFile("sample_Red.idat", b"dummy content")
        self.sample_data.update({"grn_idat": grn_file, "red_idat": red_file})

        sample = Sample.objects.create(**self.sample_data)
        self.assertTrue(sample.grn_idat.name.endswith("_Grn.idat"))
        self.assertTrue(sample.red_idat.name.endswith("_Red.idat"))

    def test_invalid_file_field(self):
        invalid_file = SimpleUploadedFile("invalid_file.txt", b"dummy content")
        self.sample_data.update({"grn_idat": invalid_file, "red_idat": invalid_file})

        sample = Sample(**self.sample_data)
        with self.assertRaises(Exception):
            sample.full_clean()


class SampleSignalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="password123")
        self.sample = Sample.objects.create(
            user=self.user,
            sample_name="TestSample",
            diagnosis="Healthy",
            age=30,
            sex=Sex.Male,
            grn_idat=SimpleUploadedFile("sample_Grn.idat", b"dummy content"),
            red_idat=SimpleUploadedFile("sample_Red.idat", b"dummy content"),
        )
        self.sample_path = join(settings.MEDIA_ROOT, "tasks", str(self.sample.id))

    @patch("slack_sdk.WebClient.chat_postMessage")
    def test_slack_notification_on_create(self, mock_slack):
        new_sample = Sample.objects.create(
            user=self.user,
            sample_name="TestSample",
            diagnosis="Disease",
            age=25,
            sex=Sex.Female,
            grn_idat=SimpleUploadedFile("sample2_Grn.idat", b"dummy content"),
            red_idat=SimpleUploadedFile("sample2_Red.idat", b"dummy content"),
        )
        mock_slack.assert_called_once_with(
            channel="mbcc",
            text=f"New sample - {new_sample.sample_name} has been added to queue by {new_sample.user.username}.",
        )

    def test_delete_sample(self):
        exists_before_delete = exists(self.sample_path)
        self.assertTrue(exists_before_delete)

        self.sample.delete()
        exists_after_delete = exists(self.sample_path)
        self.assertFalse(exists_after_delete)
