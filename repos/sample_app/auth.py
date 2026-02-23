from db import Database

class AuthService:

    def __init__(self):
        self.db = Database()

    def authenticate(self, user_id):
        user = self.db.fetch_user(user_id)
        return self.validate_user(user)

    def validate_user(self, user):
        return user is not None