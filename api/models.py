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
	    ('add', 'Allowed to add Users'),
	    ('edit_own', 'Allowed to edit own User'),
	    ('edit_any', 'Allowed to edit any User'),
	    ('delete_own', 'Allowed to delete own User'),
	    ('delete_any', 'Allowed to delete any User'),
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
	Permission.objects.exclude(name__startswith='Can'),
	widget=admin.widgets.FilteredSelectMultiple('permissions', False)
    )

    class Meta:
	model = Group
# Used for uploading media that forms part of a story
class Media(models.Model):
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=5, choices=MEDIA_TYPES)
    content = models.TextField()
    author = models.ForeignKey(User)
    author = models.ForeignKey(CustomUser)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
	    ('add', 'Allowed to add Media'),
	    ('edit_own', 'Allowed to edit own Media'),
	    ('edit_any', 'Allowed to edit any Media'),
	    ('delete_own', 'Allowed to delete own Media'),
	    ('delete_any', 'Allowed to delete any Media'),
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
    author = models.ForeignKey(CustomUser)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
	    ('edit_own', 'Allowed to edit own Story'),
	    ('edit_any', 'Allowed to edit any Story'),
	    ('delete_own', 'Allowed to delete own Story'),
	    ('delete_any', 'Allowed to delete any Story'),
        )

# Used to convert the Story model to a form in the cms
class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        # Don't show the date created field because we want that to be set automatically
        exclude = ('date_created', 'author',)
