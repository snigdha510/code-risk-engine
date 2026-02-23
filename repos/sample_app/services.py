from db import Database
from auth import AuthService

class UserService:

    def __init__(self):
        self.db = Database()
        self.auth = AuthService()

    def get_user_profile(self, user_id):
        if not self.auth.authenticate(user_id):
            return None
        return self.db.fetch_user(user_id)

    def update_user_profile(self, user_id, data):
        if not self.auth.authenticate(user_id):
            return False
        self.db.execute_query("UPDATE users")
        return True