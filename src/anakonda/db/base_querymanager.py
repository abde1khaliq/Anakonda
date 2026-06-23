class BaseQueryManager:
    def __init__(self, model, db):
        self.model = model
        self.db = db
