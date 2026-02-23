class Database:

    def connect(self):
        return "connected"

    def execute_query(self, query):
        self.connect()
        return f"executed {query}"

    def fetch_user(self, user_id):
        self.execute_query("SELECT * FROM users")
        return {"id": user_id, "name": "John"}