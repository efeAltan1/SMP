from config import db
from bson import ObjectId


# parent class for all models. collections inherit from this.
class BaseModel:

    # stores the raw document dict passed in from MongoDB or a route
    def __init__(self, data):
        self.data = data

    # overridden by subclasses to check required fields before saving
    def validate(self):
        pass

    # returns a JSON-safe copy of the document. converts ObjectId to string
    def to_dict(self):
        data_copy = self.data.copy()
        if '_id' in data_copy:
            data_copy['_id'] = str(data_copy['_id'])
        return data_copy

    # upserts the document into MongoDB. updates if exists, inserts if not
    def save(self):
        self.validate()
        collection = db[self.collection]
        collection.replace_one(
            {"_id": self.data.get("_id")},
            self.data,
            upsert=True
        )

    # fetches a single document by its ID. subclass defines which collection to look in
    @classmethod
    def find_by_id(cls, id):
        collection = db[cls.collection]
        doc = collection.find_one({"_id": ObjectId(id)})
        if doc:
            return cls(doc)
        return None

    # fetches all documents in the collection and returns them as model instances
    @classmethod
    def find_all(cls):
        collection = db[cls.collection]
        docs = collection.find()
        return [cls(doc) for doc in docs]
