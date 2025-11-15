from __future__ import annotations

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class ApiWorkflowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="securepass123")
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_upload_and_fetch_dataset(self):
        csv_data = (
            "Equipment Name,Type,Flowrate,Pressure,Temperature\n"
            "Pump-1,Pump,120,5.2,110\n"
        ).encode()
        upload = SimpleUploadedFile("test.csv", csv_data, content_type="text/csv")
        upload_url = reverse("dataset-upload")
        response = self.client.post(upload_url, {"file": upload}, format="multipart")
        self.assertEqual(response.status_code, 201)
        dataset_id = response.data["dataset"]["id"]

        list_url = reverse("dataset-list")
        list_response = self.client.get(list_url)
        self.assertEqual(list_response.status_code, 200)
        self.assertGreaterEqual(list_response.data["count"], 1)

        summary_url = reverse("dataset-summary", kwargs={"pk": dataset_id})
        summary_response = self.client.get(summary_url)
        self.assertEqual(summary_response.status_code, 200)
        self.assertEqual(summary_response.data["total_records"], 1)
