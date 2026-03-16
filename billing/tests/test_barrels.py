from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from billing.models import Provider, Barrel, InvoiceLine, Invoice


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
        
    def test_cannot_delete_billed_barrel(self):
        provider = Provider.objects.create(name="Provider A")
        
        user = User.objects.create_user(username="user_delete", password="pw", provider=provider)
        self.client.force_authenticate(user=user)
        
        invoice = Invoice.objects.create(provider=provider, issued_on="2024-01-01", invoice_no="INV-DEL")
        barrel = Barrel.objects.create(provider=provider, number="B-DEL", oil_type="Olive", liters=100, billed=True)

        InvoiceLine.objects.create(
            invoice=invoice,
            barrel=barrel,
            liters=100,
            unit_price=5.0,
            description="Test"
        )

        response = self.client.delete(f"/api/barrels/{barrel.id}/")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.assertTrue(Barrel.objects.filter(id=barrel.id).exists())