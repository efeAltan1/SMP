from .base import BaseModel


class Grade(BaseModel):
    collection = "grades"

    # Scraper writes all grade fields. validate() is a no-op here since
    # data integrity is enforced at scrape time, not at save time.
    def validate(self):
        pass
