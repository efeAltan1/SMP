from .base import BaseModel

class Subject(BaseModel):
    collection = "subjects"


# Checks to see whether name and credits exist in self.data
def validate(self):
    if 'name' not in self.data:
        raise ValueError('Name required.')
    if 'credits' not in self.data:
        raise ValueError('Credits required.') 