from django.db import models
from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib import admin
from django.template.defaultfilters import slugify
from google.appengine.api import search
from datetime import datetime

MEDIA_TYPES = (
    ('audio', 'audio'),
    ('video', 'video'),
    ('text', 'text'),
    ('image', 'image'),
)

STORY_STATUSES = (
    ('draft', 'draft'),
    ('published', 'published'),
)

class CustomUser(User):
    class Meta:
        proxy = True
        permissions = (
            ('wina_add_user', 'Allowed to add Users'),
            ('wina_edit_own_user', 'Allowed to edit own User'),
            ('wina_edit_any_user', 'Allowed to edit any User'),
            ('wina_deactivate_any_user', 'Allowed to deactivate any User'),
            ('wina_activate_any_user', 'Allowed to activate any User'),
        )

# Used to convert the User model to a form in the cms
class CustomUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        # There's more fields we want to exclude than include so just list the ones we want
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'groups']

    # Override the save method to add our custom fields in correctly
    def save(self, commit=True):
        user_form = super(CustomUserForm, self).save(commit=False)

        # Save the users password, this automatically hashes it
        user_form.set_password(user_form.password)

        if commit:
            user_form.save()

        return user_form

class CustomGroup(Group):
    class Meta:
        proxy = True
        permissions = (
            ('wina_add_group', 'Allowed to add a Group'),
            ('wina_edit_group', 'Allowed to edit a Group'),
            ('wina_delete_group', 'Allowed to delete a Group'),
        )

# Used to convert the Group model to a form in the cms
class CustomGroupForm(forms.ModelForm):
    # Only show our own permissions that prefixed with wina_ and not django's defaults
    permissions = forms.ModelMultipleChoiceField(
        Permission.objects.filter(codename__startswith='wina_'),
        widget=admin.widgets.FilteredSelectMultiple('permissions', False)
    )

    class Meta:
        model = CustomGroup

# Used for uploading media that forms part of a story
class Media(models.Model):
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    content = models.TextField(blank=True)
    author = models.ForeignKey(CustomUser)
    date_created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField()

    class Meta:
        permissions = (
            ('wina_add_media', 'Allowed to add Media'),
            ('wina_edit_own_media', 'Allowed to edit own Media'),
            ('wina_edit_any_media', 'Allowed to edit any Media'),
            ('wina_delete_own_media', 'Allowed to delete own Media'),
            ('wina_delete_any_media', 'Allowed to delete any Media'),
        )

    # Override the save method
    def save(self, *args, **kwargs):
        # Slugify the title
        self.slug = slugify(self.title)

        super(Media, self).save(*args, **kwargs)

        # Create the search document
        document = search.Document(
            doc_id='media:%s' % self.id,
            fields=[
                search.AtomField(name='doc_type', value='media'),
                search.AtomField(name='type', value=self.type),
                search.TextField(name='title', value=self.title),
                search.AtomField(name='content', value=self.content),
                search.NumberField(name='author_id', value=self.author.id),
                search.TextField(name='author_username', value=self.author.username),
                search.TextField(name='author_first_name', value=self.author.first_name),
                search.TextField(name='author_last_name', value=self.author.last_name),
                search.DateField(name='date_created', value=datetime.now()),
                search.AtomField(name='slug', value=self.slug),
            ]
        )

        # Store it in our stories-and-media index
        index = search.Index(name='stories-and-media')
        index.put(document)

    # Override the delete method so we can remove docs from the search index
    def delete(self, *args, **kwargs):
        super(Media, self).delete(*args, **kwargs)

        # Delete the entry from the stories-and-media index
        index = search.Index(name='stories-and-media')
        index.delete('media:%s' % self.id)

# Used to convert the media model to a form in the cms
class MediaForm(forms.ModelForm):
    file = forms.FileField(required=False)

    class Meta:
        model = Media
        # Don't show the date created field because we want that to be set automatically
        exclude = ('date_created', 'author', 'slug',)

    # Custom validation
    def clean(self):
        # Import the ValidationError exception from Django
        from django.core.exceptions import ValidationError

        # Get the data that has already been passed through Django's validation
        cleaned_data = super(MediaForm, self).clean()

        # Check the type is valid
        if cleaned_data['type'] in ['audio', 'video', 'image'] and cleaned_data['file'] is None:
            raise ValidationError('When the type is audio, video or image you must specify a file to upload')

        # Check that when the text type is chosen some content is present
        elif cleaned_data['type'] == 'text' and cleaned_data['content'] == '':
            raise ValidationError('When the type is text you must specify content to upload')

        return cleaned_data


# Used for creating a story that contains multiple bits of media
class Story(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(CustomUser)
    status = models.CharField(max_length=9, choices=STORY_STATUSES, default='draft')
    slug = models.SlugField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('wina_add_story', 'Allowed to add a Story'),
            ('wina_edit_own_story', 'Allowed to edit own Story'),
            ('wina_edit_any_story', 'Allowed to edit any Story'),
            ('wina_delete_own_story', 'Allowed to delete own Story'),
            ('wina_delete_any_story', 'Allowed to delete any Story'),
        )

    # Override the save method
    def save(self, *args, **kwargs):
        # Slugify the title
        self.slug = slugify(self.title)

        super(Story, self).save(*args, **kwargs)

        # Create the search document
        document = search.Document(
            doc_id='story:%s' % self.id,
            fields=[
                search.AtomField(name='doc_type', value='story'),
                search.AtomField(name='type', value='story'),
                search.TextField(name='title', value=self.title),
                search.HtmlField(name='content', value=self.content),
                search.NumberField(name='author_id', value=self.author.id),
                search.TextField(name='author_username', value=self.author.username),
                search.TextField(name='author_first_name', value=self.author.first_name),
                search.TextField(name='author_last_name', value=self.author.last_name),
                search.DateField(name='date_created', value=datetime.now()),
                search.AtomField(name='status', value=self.status),
                search.AtomField(name='slug', value=self.slug),
            ]
        )

        # Store it in our stories-and-media index
        index = search.Index(name='stories-and-media')
        index.put(document)

    # Override the delete method so we can remove docs from the search index
    def delete(self, *args, **kwargs):
        id = self.id

        super(Story, self).delete(*args, **kwargs)

        # Delete the entry from the stories-and-media index
        index = search.Index(name='stories-and-media')
        index.delete('story:%s' % id)

# Used to convert the Story model to a form in the cms
class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        # Don't show the date created field because we want that to be set automatically
        exclude = ('date_created', 'author', 'slug',)
