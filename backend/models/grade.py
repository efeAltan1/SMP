from .base import BaseModel


class Grade(BaseModel):
    collection = "grades"

    def validate(self):
        required = ['subject_id', 'title', 'score', 'weight']
        for field in required:
            if field not in self.data:
                raise ValueError(f'{field} is required.')
