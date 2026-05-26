from .base import BaseModel


class Announcement(BaseModel):
    collection = "announcements"


# Validating all required announcement fields before saving to MongoDB. Raises ValueError if any are missing.  
    def validate(self):
        required = ['title', 'content', 'date', 'tag']
        for field in required:
            if field not in self.data:
                raise ValueError(f'{field} is required.')
