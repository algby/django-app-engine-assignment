from django.db import models
from django import forms
from django.contrib.auth.models import User

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
    author = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('add', 'Can add Media'),
            ('edit_own', 'Can edit own Media'),
            ('edit_any', 'Can edit any Media'),
            ('delete_own', 'Can delete own Media'),
            ('delete_any', 'Can delete any Media'),
        )

    def __unicode__(self):
        return self.title

# Used to convert the media model to a form in the cms
class MediaForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = Media
        # Don't show the date created field because we want that to be set automatically
        exclude = ('date_created', 'content', 'author',)

# Used for creating a story that contains multiple bits of media
class Story(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('add', 'Can add Story'),
            ('edit_own', 'Can edit own Story'),
            ('edit_any', 'Can edit any Story'),
            ('delete_own', 'Can delete own Story'),
            ('delete_any', 'Can delete any Story'),
        )

# Used to convert the Story model to a form in the cms
class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        # Don't show the date created field because we want that to be set automatically
        exclude = ('date_created', 'author',)

# Used to convert the Story model to a form in the cms
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        # There's more fields we want to exclude than include so just list the ones we want
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'groups']

    # Override the save method to add our custom fields in correctly
    def save(self, commit=True):
        user_form = super(UserForm, self).save(commit=False)

        # Save the users password, this automatically hashes it
        user_form.set_password(user_form.password)

        if commit:
            user_form.save()

        return user_form
