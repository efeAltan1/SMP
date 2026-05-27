from .base import BaseModel


class Subject(BaseModel):
    collection = "subjects"

    # Scraper writes all subject/schedule fields. validate() is a no-op here.
    def validate(self):
        pass
