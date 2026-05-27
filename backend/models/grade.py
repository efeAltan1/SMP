from .base import BaseModel


class Grade(BaseModel):
    collection = "grades"

# Validating all required grade fields before saving to MongoDB. Raises ValueError if any are missing.
    def validate(self):
        required = ['subject_id', 'title', 'score', 'weight']
        for field in required:
            if field not in self.data:
                raise ValueError(f'{field} is required.')
