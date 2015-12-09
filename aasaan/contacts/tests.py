from django.test import TestCase
from contacts.models import Contact

# Create your tests here.

class ContactTests(TestCase):
    """Tests for contacts model"""

    def test_str(self):
        contact = Contact(first_name='Deepak', last_name='Kumaran')
        self.assertEquals(str(contact), 'Deepak Kumaran',)
