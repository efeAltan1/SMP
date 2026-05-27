from .base import BaseModel


class Attendance(BaseModel):
    collection = "attendance"

    # Scraper writes all attendance fields. validate() is a no-op here.
    def validate(self):
        pass
