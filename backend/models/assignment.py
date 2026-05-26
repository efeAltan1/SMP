from .base import BaseModel


class Assignment(BaseModel):
    collection = "assignments"


# Validating all required assignmentfields before saving to MongoDB. Raises ValueError if any are missing.
    def validate(self):
        required = ['subject_id', 'title', 'deadline', 'priority', 'status']
        for field in required:
            if field not in self.data:
                raise ValueError(f'{field} is required.')
