from .base import BaseModel

class Subject(BaseModel):
    collection = "subjects"


# Validating all required subject fields before saving to MongoDB. Raises ValueError if any are missing.
def validate(self):
    if 'name' not in self.data:
        raise ValueError('Name required.')
    if 'credits' not in self.data:
        raise ValueError('Credits required.') 