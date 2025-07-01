from surrealdb import Surreal
from uuid import uuid4, UUID
import re

USER_REGISTRY_DB_URL = "ws://database:8000/rpc"

class UserRegistry:
    _user_id : UUID

    def __init__(self):
        self.db = Surreal(USER_REGISTRY_DB_URL)
        self.db.signin({"username": 'root', "password": 'root'})
        self.db.use("user_registry", "user_registry_master")

    def __del__(self):
        self.db.close()

    def create_user(self, username: str, password: str):
        username = re.sub(r'[^a-zA-Z0-9]', '', username).lower()
        password = re.sub(r'[^a-zA-Z0-9]', '', password)
        query_result = self.db.query(
            "SELECT username FROM local_user WHERE username == $input_username LIMIT 1;",
            { "input_username": username })
        if len(query_result) > 0:
            raise ValueError(f"User '{username}' already exists.")

        self.db.create(
            "local_user",
            {
                "username": username,
                "password": password,
                "user_id": uuid4(),
            },
        )

    def user_login(self, username: str, password: str):
        username = re.sub(r'[^a-zA-Z0-9]', '', username).lower()
        password = re.sub(r'[^a-zA-Z0-9]', '', password)
        query_result = self.db.query(
            "SELECT username, user_id, password FROM local_user WHERE username == $input_username LIMIT 1;",
            { "input_username": username })
        if len(query_result) == 0:
            raise ValueError(f"User '{username}' does not exist.")
        user_data = query_result[0]
        if user_data['password'] != password:
            raise ValueError("Incorrect password.")
        
        self._user_id = user_data['user_id']

    def get_username(self) -> str:  
        if not hasattr(self, '_user_id'):
            raise ValueError("User ID is not set. Please log in first.")
    
        query_result = self.db.query(
            "SELECT username FROM local_user WHERE user_id == $input_user_id LIMIT 1;",
            { "input_user_id": self._user_id })
        
        if len(query_result) == 0:
            raise ValueError("User not found.")
        
        return query_result[0]['username']
    
    def get_user_id(self) -> UUID:
        if not hasattr(self, '_user_id'):
            raise ValueError("User ID is not set. Please log in first.")
        
        return self._user_id
