from .base import BaseModel


class Exam(BaseModel):
    collection = "exams"

    def validate(self):
        required = ['subject_id', 'title', 'date', 'location', 'duration']
        for field in required:
            if field not in self.data:
                raise ValueError(f'{field} is required.')
