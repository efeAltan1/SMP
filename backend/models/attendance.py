from .base import BaseModel


class Attendance(BaseModel):
    collection = "attendance"

    def validate(self):
        required = ['subject_id', 'date', 'status']
        for field in required:
            if field not in self.data:
                raise ValueError(f'{field} is required.')
