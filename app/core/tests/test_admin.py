"""
Tests for the Django admin modifications.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test.client import Client

class AdminSiteTests(TestCase):
    """Tests for Django admin."""

    def setUp(self):
        """Set up user and client."""
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@example.com',
            'admin'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )

    def test_users_list(self):
        """ Test that users are listed on the page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_edit_user_page(self):
        """Test the edit user page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, self.user.email)
        self.assertContains(res, self.user.name)

    def test_create_user_page(self):
        """Test the create user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
