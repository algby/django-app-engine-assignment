from django.db import models
from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib import admin

MEDIA_TYPES = (
    ('audio', 'audio'),
    ('video', 'video'),
    ('text', 'text'),
    ('image', 'image'),
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

# Used to convert the Group model to a form in the cms
class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        Permission.objects.filter(codename__startswith='wina_'),
        widget=admin.widgets.FilteredSelectMultiple('permissions', False)
    )

    class Meta:
        model = Group

# Used for uploading media that forms part of a story
class Media(models.Model):
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    content = models.TextField(blank=True)
    author = models.ForeignKey(CustomUser)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('wina_add_media', 'Allowed to add Media'),
            ('wina_edit_own_media', 'Allowed to edit own Media'),
            ('wina_edit_any_media', 'Allowed to edit any Media'),
            ('wina_delete_own_media', 'Allowed to delete own Media'),
            ('wina_delete_any_media', 'Allowed to delete any Media'),
        )

    def __unicode__(self):
        return self.title

# Used to convert the media model to a form in the cms
class MediaForm(forms.ModelForm):
    file = forms.FileField()

    class Meta:
        model = Media
        # Don't show the date created field because we want that to be set automatically
	exclude = ('date_created', 'author', 'content',)

# Used for creating a story that contains multiple bits of media
class Story(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(CustomUser)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ('wina_add_story', 'Allowed to add a Story'),
            ('wina_edit_own_story', 'Allowed to edit own Story'),
            ('wina_edit_any_story', 'Allowed to edit any Story'),
            ('wina_delete_own_story', 'Allowed to delete own Story'),
            ('wina_delete_any_story', 'Allowed to delete any Story'),
        )

# Used to convert the Story model to a form in the cms
class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        # Don't show the date created field because we want that to be set automatically
        exclude = ('date_created', 'author',)
