from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from billing.models import Provider, Invoice, Barrel, InvoiceLine

User = get_user_model()

class InvoiceIntegrationTests(APITestCase):

    def test_adding_barrel_to_different_provider_invoice_fails(self):
        provider_a = Provider.objects.create(name="Provider A")
        provider_b = Provider.objects.create(name="Provider B")

        invoice_a = Invoice.objects.create(provider=provider_a, issued_on="2024-01-01")

        barrel_b = Barrel.objects.create(
            provider=provider_b,
            number="B-001",
            oil_type="OLIVA", 
            liters=100,
            billed=False
        )

        user_a = User.objects.create_user(
            username="user_a", 
            password="password123", 
            provider=provider_a
        )
        self.client.force_authenticate(user=user_a)


        url = f"/api/invoices/{invoice_a.id}/add-line/"
        
      
        payload = {
            "barrel_id": barrel_b.id,
            "liters": 100,
            "unit_price_per_liter": 5.50
        }

        response = self.client.post(url, payload, format="json")


        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.assertEqual(InvoiceLine.objects.count(), 0)

        barrel_b.refresh_from_db()
        self.assertFalse(barrel_b.billed)