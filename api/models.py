from django.db import models
from django.forms import ModelForm

MEDIA_TYPES = (
    ('audio', 'audio'),
    ('video', 'video'),
    ('text', 'text'),
    ('image', 'image'),
)

# Used for uploading media that forms part of a story
class Media(models.Model):
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

# Used to convert the media model to a form in the cms
class MediaForm(ModelForm):
    class Meta:
        model = Media
        # Don't show the date created field because we want that to be set automatically
        exclude = ('date_created')