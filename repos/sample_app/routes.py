from services import UserService

class UserRoutes:

    def __init__(self):
        self.service = UserService()

    def get_profile(self, user_id):
        return self.service.get_user_profile(user_id)

    def update_profile(self, user_id, data):
        return self.service.update_user_profile(user_id, data)