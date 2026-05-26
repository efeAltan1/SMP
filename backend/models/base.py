from config import db
from bson import ObjectId


# Parent class for all models. Subclasses inherit from this and implement their own validate() method to check required fields. 
class BaseModel:

    # Stores raw data. Subclasses inherit this and their own methods to validate and save to MongoDB.
    def __init__(self, data):
        self.data = data

    # Empty class that subclasses override to validate required fields.
    def validate(self):
        pass

    # Returns a JSON copy of the data.
    def to_dict(self):
        data_copy = self.data.copy()
        if '_id' in data_copy:
            data_copy['_id'] = str(data_copy['_id'])
        return data_copy

    # Upserts the document in MongoDB. If it exists, update. If it doesn't, insert.
    def save(self):
        self.validate()
        collection = db[self.collection]
        collection.replace_one({"_id": self.data.get("_id")}, self.data, upsert=True)

    # Fetches single document in the collection by ID. 
    @classmethod
    def find_by_id(cls, id):
        collection = db[cls.collection]
        doc = collection.find_one({"_id": ObjectId(id)})
        if doc:
            return cls(doc)
        return None

    # Fetches all documents in the collection.
    @classmethod
    def find_all(cls):
        collection = db[cls.collection]
        docs = collection.find()
        return [cls(doc) for doc in docs]
