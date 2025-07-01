from surrealdb import Surreal

USER_REGISTRY_DB_URL = "ws://database:8000/rpc"

class BackendManager:
    def __init__(self):
        self.user_registry_db = Surreal(USER_REGISTRY_DB_URL)
        self.user_registry_db.signin({"username": 'root', "password": 'root'})
        self.user_registry_db.use("user_registry", "user_registry_master")
