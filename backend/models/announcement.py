from .base import BaseModel


class Announcement(BaseModel):
    collection = "announcements"

    # Scraper writes all announcement fields. validate() is a no-op here.
    def validate(self):
        pass
