from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from billing.models import Provider, Barrel

User = get_user_model()

class ProviderEndpointTests(APITestCase):

    def setUp(self):
        self.provider_a = Provider.objects.create(name="Provider A", tax_id="A-111")
        self.provider_b = Provider.objects.create(name="Provider B", tax_id="B-222")

        self.user_a = User.objects.create_user(username="user_a", password="pw", provider=self.provider_a)
        self.admin_user = User.objects.create_superuser(username="admin", password="pw", email="admin@test.com")

       
        Barrel.objects.create(provider=self.provider_a, number="B-01", oil_type="Olive", liters=100, billed=True)

        Barrel.objects.create(provider=self.provider_a, number="B-02", oil_type="Olive", liters=50, billed=False)

    def test_superuser_sees_all_providers(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/api/providers/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Provider.objects.count())  

    def test_normal_user_sees_only_own_provider(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/api/providers/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.provider_a.id)

    def test_normal_user_cannot_access_other_provider_detail(self):
        self.client.force_authenticate(user=self.user_a)

        response = self.client.get(f"/api/providers/{self.provider_b.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_provider_liters_calculations(self):
        self.client.force_authenticate(user=self.user_a)
        response = self.client.get(f"/api/providers/{self.provider_a.id}/")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["billed_liters"], 100)
        self.assertEqual(response.data["liters_to_bill"], 50)