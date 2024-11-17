from django.test import TestCase, Client
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
from .models import BlogPost
import json

class BlogAppTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()

    def test_index_view_requires_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)  # Redirect to login page

        self.client.login(username='testuser', password='password')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)  # Should access the index

    def test_user_login(self):
        response = self.client.post('/login', {'username': 'testuser', 'password': 'password'})
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_user_signup(self):
        response = self.client.post('/signup', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password',
            'repeatPassword': 'password',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after signup
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_logout(self):
        self.client.login(username='testuser', password='password')
        response = self.client.get('/logout')
        self.assertEqual(response.status_code, 302)  # Redirect after logout

    def test_generate_blog_invalid_method(self):
        response = self.client.get('/generate-blog')
        self.assertEqual(response.status_code, 405)  # Method not allowed

    @patch('blog_generator.views.YouTube')
    @patch('blog_generator.views.Groq')
    def test_generate_blog_success(self, mock_groq, mock_youtube):
        self.client.login(username='testuser', password='password')

        # Mock YouTube object
        mock_youtube.return_value.title = "Test Video Title"
        mock_youtube.return_value.captions = {'en': MagicMock()}
        mock_youtube.return_value.captions['en'].save_captions = MagicMock()

        # Mock Groq response
        mock_chat_completion = MagicMock()
        mock_chat_completion.choices = [MagicMock()]
        mock_chat_completion.choices[0].message.content = "Generated Blog Content"
        mock_groq.return_value.chat.completions.create.return_value = mock_chat_completion

        data = {
            'link': 'https://www.youtube.com/watch?v=testvideo'
        }
        response = self.client.post('/generate-blog', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('content', response.json())

        # Check if blog post was created
        self.assertTrue(BlogPost.objects.filter(user=self.user).exists())

    def test_blog_list_view(self):
        BlogPost.objects.create(
            user=self.user,
            youtube_title="Test Title",
            youtube_link="https://www.youtube.com/watch?v=ba58WZd0NaE",
            generated_content="Test Content"
        )
        self.client.login(username='testuser', password='password')
        response = self.client.get('/blog-list')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Title")

    def test_blog_details_view(self):
        blog = BlogPost.objects.create(
            user=self.user,
            youtube_title="Test Title",
            youtube_link="https://www.youtube.com/watch?v=ba58WZd0NaE",
            generated_content="Test Content"
        )
        self.client.login(username='testuser', password='password')
        response = self.client.get(f'/blog-details/{blog.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Title")

    def test_blog_details_view_unauthorized_user(self):
        another_user = User.objects.create_user(username='anotheruser', password='password')
        blog = BlogPost.objects.create(
            user=another_user,
            youtube_title="Test Title",
            youtube_link="https://www.youtube.com/watch?v=ba58WZd0NaE",
            generated_content="Test Content"
        )
        self.client.login(username='testuser', password='password')
        response = self.client.get(f'/blog-details/{blog.id}/')
        self.assertEqual(response.status_code, 302)