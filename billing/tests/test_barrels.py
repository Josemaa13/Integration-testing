from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from billing.models import Provider, Barrel

User = get_user_model()

class BarrelIntegrationTests(APITestCase):

    def test_create_barrel_ignores_provider_in_payload(self):
        provider_a = Provider.objects.create(name="Provider A")
        provider_b = Provider.objects.create(name="Provider B")

        user_a = User.objects.create_user(
            username="user_a", 
            password="password123", 
            provider=provider_a
        )
        self.client.force_authenticate(user=user_a)

        url = "/api/barrels/"
        
        payload = {
            "number": "B-999",
            "oil_type": "OLIVA",
            "liters": 200,
            # TODO hack :)
            "provider": provider_b.id  
        }

        response = self.client.post(url, payload, format="json")

       
       
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
        created_barrel = Barrel.objects.get(number="B-999")
        
        
        self.assertEqual(created_barrel.provider_id, provider_a.id)
        
        
        self.assertNotEqual(created_barrel.provider_id, provider_b.id)