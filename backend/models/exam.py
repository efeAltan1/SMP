from .base import BaseModel


class Exam(BaseModel):
    collection = "exams"

    # Scraper writes all exam fields. validate() is a no-op here.
    def validate(self):
        pass
