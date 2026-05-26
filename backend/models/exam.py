from .base import BaseModel


# Accessing upcoming exams. 
class Exam(BaseModel):
    collection = "exams"

    def validate(self):
        required = ['subject_id', 'title', 'date', 'location', 'hour']
        for field in required:
            if field not in self.data:
                raise ValueError(f'{field} is required.')
