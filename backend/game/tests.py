from django.test import TestCase

# Create your tests here.
from unittest.mock import patch, MagicMock
from game.gemini_utils import generate_question, QuestionSchema

class GeminiUtilsTest(TestCase):

    # @patch intercepts the call to the client inside your utils file
    @patch("game.gemini_utils.client.models.generate_content")
    def test_generate_question_success(self, mock_generate):
        # 1. Setup the "Fake" Response from Gemini
        # We need an object that has a .text attribute containing JSON
        mock_response = MagicMock()
        mock_response.text = """
        {
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5", "6"],
            "answer": "4",
            "explanation": "Math is fun."
        }
        """
        mock_generate.return_value = mock_response

        # 2. Call your function
        result = generate_question(level=1)

        # 3. Verify the result is a valid Schema
        self.assertIsInstance(result, QuestionSchema)
        self.assertEqual(result.question, "What is 2 + 2?")
        self.assertEqual(result.answer, "4")
        
        # 4. Verify we actually called the mock with the right prompt
        # (Optional, but good for debugging)
        args, kwargs = mock_generate.call_args
        self.assertIn("level 1", kwargs['contents'])

    @patch("game.gemini_utils.client.models.generate_content")
    def test_generate_question_failure(self, mock_generate):
        """Test what happens if Gemini returns garbage"""
        mock_response = MagicMock()
        mock_response.text = "I cannot answer this." # Not JSON!
        mock_generate.return_value = mock_response

        # We expect our function to raise a ValueError (as defined in your utils)
        with self.assertRaises(ValueError):
            generate_question(level=1)