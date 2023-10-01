import sys
import os
import bcrypt




# Add the parent directory of BS-PMC-2023-Team13 to the Python path
project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_directory)

# Rest of your test code
import pytest
import website
from website import create_app
from flask import app, request

from website.forms import UpdateUserForm

class TestAboutPage:
    @pytest.fixture
    def app(self):
        """Create and configure a new Flask application for each test."""
        app = create_app()
        yield app

    @pytest.fixture
    def client(self, app):
        """Create a test client for the Flask application."""
        return app.test_client()

    def test_about(self, client):
        """Test the About Us page.

        Sends a GET request to the '/about' route and asserts various conditions on the response.

        Assertions:
        - Response status code should be 200 (OK).
        - The expected text should be present in the response data.
        """
        response = client.get('/about')

        assert response.status_code == 200
        assert "עלינו" in response.data.decode('utf-8')
        assert "ברוכים הבאים למחסן של המחלקה לתקשורת חזותית!" in response.data.decode('utf-8')
        assert "&copy; 2023 המחלקה להנדסת תוכנה." in response.data.decode('utf-8')
        assert "האתר WH-Organization נוצר על מנת ליעיל את אופן השאלות הציוד בין אנשי המחלקה לתקשורת" in response.data.decode('utf-8')
        assert "חזותית לבין מנהלי מחסן המחלקה. האתר מספק פלטפורמה נוחה לפתיחת בקשות לאישורם ולמעקבם." in response.data.decode('utf-8')
        assert "מפתחי האתר: Klassen Eva-Maria , Moiseyev Ester,Dali Yarden, Abitbul Gilad" in response.data.decode('utf-8')
        assert "אנשי מחסן המחלקה:  {המייל של שי }" in response.data.decode('utf-8')


    
