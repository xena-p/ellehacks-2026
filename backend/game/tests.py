from django.test import TestCase, Client
from django.contrib.auth import get_user_model
# Create your tests here.
from unittest.mock import patch, MagicMock
from game.gemini_utils import generate_question, QuestionSchema

User = get_user_model()

class QuizAuthTest(TestCase):
    def setUp(self):
        # 1. Create a specific test user with Level 3
        self.user = User.objects.create_user(username="pro_gamer", password="password")
        self.user.level = 3
        self.user.save()
        self.client = Client()

    # IMPORTANT: Patch 'game.api.generate_question' because that is where it is imported!
    @patch("game.api.generate_question") 
    def test_quiz_uses_logged_in_level(self, mock_generate):
        # Setup mock return value so the API doesn't crash
        mock_generate.return_value = {
            "question": "Mock Q", "options": ["A"], "answer": "A", "explanation": "Exp"
        }

        # 2. FORCE LOGIN (This bypasses the password check for testing)
        self.client.force_login(self.user)

        # 3. Hit the endpoint
        response = self.client.get("/api/generate-quiz")

        # 4. THE MOMENT OF TRUTH: 
        # Did it call generate_question(3)? Or did it fail and default to (1)?
        mock_generate.assert_called_with(3)
        
        print("\n✅ SUCCESS: The API correctly identified the user is Level 3!")
        
class GeminiUtilsTest(TestCase):

    # @patch intercepts the call to the client inside your utils file
    @patch("game.gemini_utils.client.models.generate_content")
    def test_generate_question_success(self, mock_generate):
        # 1. Mock the response
        mock_response = MagicMock()
        mock_response.text = '{"question": "Q", "options": ["A"], "answer": "A", "explanation": "E"}'
        mock_generate.return_value = mock_response

        # 2. Call with LEVEL 3 this time
        result = generate_question(level=3)

        # 3. Verify we sent the HARD prompt
        args, kwargs = mock_generate.call_args
        sent_prompt = kwargs['contents']
        
        # Check that your difficulty map text is inside the prompt
        self.assertIn("harder", sent_prompt) 
        self.assertIn("involves reasoning", sent_prompt)

    @patch("game.gemini_utils.client.models.generate_content")
    def test_generate_question_failure(self, mock_generate):
        """Test what happens if Gemini returns garbage"""
        mock_response = MagicMock()
        mock_response.text = "I cannot answer this." # Not JSON!
        mock_generate.return_value = mock_response

        # We expect our function to raise a ValueError (as defined in your utils)
        with self.assertRaises(ValueError):
            generate_question(level=1)