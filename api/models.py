from django.db import models
from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib import admin
from django.template.defaultfilters import slugify
from google.appengine.api import search
from datetime import datetime
from google.appengine.ext import ndb

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

# The model for users of the site
class WinaUser(User):
    class Meta:
        # Proxy django's user model so we can add our own permissions
        proxy = True
        permissions = (
            ('wina_add_user', 'Allowed to add Users'),
            ('wina_edit_own_user', 'Allowed to edit own User'),
            ('wina_edit_any_user', 'Allowed to edit any User'),
            ('wina_deactivate_any_user', 'Allowed to deactivate any User'),
            ('wina_activate_any_user', 'Allowed to activate any User'),
        )

# Used to convert the User model to a form in the cms
class CmsUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = WinaUser
        # There's more fields we want to exclude than include so just list the ones we want
        fields = ['username', 'first_name', 'last_name', 'email', 'groups', 'is_staff', 'is_superuser', 'is_active']

    # Override the save method to add our custom fields in correctly
    def save(self, commit=True):
        user_form = super(CmsUserForm, self).save(commit=False)

        # Hash the users password
        user_form.set_password(user_form.password)

        if commit:
            user_form.save()

        return user_form

# Used to convert the User model to a form on the frontend
class FrontEndUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = WinaUser
        # There's more fields we want to exclude than include so just list the ones we want
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    # Override the save method to add our custom fields in correctly
    def save(self, commit=True):
        user_form = super(FrontEndUserForm, self).save(commit=False)

        # Hash the users password
        user_form.set_password(user_form.password)

        if commit:
            user_form.save()

        return user_form

# The model for permission groups
class WinaGroup(Group):
    class Meta:
        # Proxy django's group model so we can add our own permissions
        proxy = True
        permissions = (
            ('wina_add_group', 'Allowed to add a Group'),
            ('wina_edit_group', 'Allowed to edit a Group'),
            ('wina_delete_group', 'Allowed to delete a Group'),
        )

# Used to convert the Group model to a form in the cms
class WinaGroupForm(forms.ModelForm):
    # Only show our own permissions that prefixed with wina_ and not django's defaults
    permissions = forms.ModelMultipleChoiceField(
        Permission.objects.filter(codename__startswith='wina_'),
        widget=admin.widgets.FilteredSelectMultiple('permissions', False)
    )

    class Meta:
        model = WinaGroup

# Used for uploading media that forms part of a story
class Media(models.Model):
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    content = models.TextField(blank=True)
    author = models.ForeignKey(WinaUser)
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
    author = models.ForeignKey(WinaUser)
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

    def get_votes(self):
        votes = StoryVote.get_by_id('StoryVote:%s' % self.id)
        return {
            'upvotes': votes.upvotes,
            'downvotes': votes.downvotes,
            'total': votes.total,
        }

    @ndb.transactional
    def upvote(self):
        votes = StoryVote.get_by_id('StoryVote:%s' % self.id)
        votes.upvotes += 1
        votes.total += 1
        return votes.put()

    @ndb.transactional
    def downvote(self):
        votes = StoryVote.get_by_id('StoryVote:%s' % self.id)
        votes.downvotes += 1
        votes.total -= 1
        return votes.put()

    def init_vote_entity(self):
        story_vote = StoryVote(
            id='StoryVote:%s' % self.id,
            upvotes=0,
            downvotes=0,
            total=0,
            status=self.status
        )
        return story_vote.put()

    @ndb.transactional
    def update_vote_status(self):
        # Make sure the status is up to date in the datastore but keep the votes the same
        votes = StoryVote.get_by_id('StoryVote:%s' % self.id)
        votes = StoryVote(
            id='StoryVote:%s' % self.id,
            upvotes=votes.upvotes,
            downvotes=votes.downvotes,
            total=votes.total,
            status=self.status
        )
        return votes.put()

    # Override the save method
    def save(self, *args, **kwargs):
        # Slugify the title
        self.slug = slugify(self.title)

        # This will only run on the first creation of the model as we don't want to
        # keep setting the vote counts to 0!
        just_created = True if not self.pk else False

        # Save it to the database
        super(Story, self).save(*args, **kwargs)

        # This has to be run after the save so we have access to the id
        if just_created:
            # Create the initial StoryVote object in the datastore
            self.init_vote_entity()

        # Otherwise we can just update the status property
        else:
            self.update_vote_status()

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

class StoryVote(ndb.Model):
    upvotes = ndb.IntegerProperty()
    downvotes = ndb.IntegerProperty()
    total = ndb.IntegerProperty()
    status = ndb.StringProperty()
