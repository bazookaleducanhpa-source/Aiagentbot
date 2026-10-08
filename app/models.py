from typing import Literal
from pydantic import BaseModel, Field, model_validator

class Campaign(BaseModel):
    topic: str = Field(min_length=3, max_length=200)
    audience: str = Field(default='English-speaking viewers who enjoy imaginative AI short stories', min_length=3, max_length=300)
    duration: int = Field(default=45, ge=15, le=90)
    platforms: list[Literal['youtube', 'tiktok']] = Field(default_factory=lambda: ['youtube', 'tiktok'], min_length=1, max_length=2)
    @model_validator(mode='after')
    def unique_platforms(self):
        self.platforms = list(dict.fromkeys(self.platforms))
        return self

class Scene(BaseModel):
    heading: str = Field(min_length=1, max_length=100)
    narration: str = Field(min_length=1, max_length=500)
    visual: str = Field(default='', max_length=300)

class Script(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=3000)
    hashtags: list[str] = Field(default_factory=list, max_length=10)
    made_for_kids: bool = False
    scenes: list[Scene] = Field(min_length=2, max_length=10)

class SourceInput(BaseModel):
    platform: Literal['youtube', 'tiktok']
    url: str = Field(max_length=500)
    title: str = Field(min_length=1, max_length=300)
    summary: str = Field(default='', max_length=2000)
    views: int = Field(default=0, ge=0)
    published_at: str
    @model_validator(mode='after')
    def check_url_date(self):
        from urllib.parse import urlparse
        from datetime import datetime
        u = urlparse(self.url)
        domains = {'youtube': ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be'), 'tiktok': ('tiktok.com', 'www.tiktok.com', 'vm.tiktok.com', 'vt.tiktok.com')}
        if u.scheme != 'https' or u.hostname not in domains[self.platform]:
            raise ValueError('Use an HTTPS link from the selected platform.')
        d = datetime.fromisoformat(self.published_at.replace('Z', '+00:00'))
        if d.tzinfo is None:
            raise ValueError('Include a timezone, for example 2026-10-08T10:00:00+07:00.')
        return self

class Publication(BaseModel):
    platform: Literal['youtube', 'tiktok']
    tiktok_mode: Literal['manual', 'buffer'] | None = None
    scheduled_at: str | None = None
    privacy: Literal['private', 'unlisted', 'public'] = 'private'
    @model_validator(mode='after')
    def validate_time(self):
        if self.scheduled_at:
            from datetime import datetime, timezone
            d = datetime.fromisoformat(self.scheduled_at.replace('Z', '+00:00'))
            if d.tzinfo is None or d <= datetime.now(timezone.utc):
                raise ValueError('Schedule must be in the future and include a timezone.')
            self.scheduled_at = d.astimezone(timezone.utc).isoformat()
        return self

class Feedback(BaseModel):
    views: int = Field(ge=0)
    retention: float = Field(ge=0, le=100)
    note: str = Field(default='', max_length=1500)
