from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as logout_user
from django.contrib import messages
from django.core.urlresolvers import reverse

from api.models import Media
from api.models import MediaForm

from modules import cloudstorage as gcs

# Render the CMS home page if the user is logged in
@login_required
def index(request):
    return render(request, 'cms/index.html', {'title': 'Welcome, %s' % request.user})

# Log out the user and redirect to them to /
def logout(request):
    # Logout the user
    logout_user(request)

    # Redirect them to the home page
    return redirect('/')

# Render the cms media home page if the user is logged in
@login_required
def media(request):
    media = Media.objects.all()

    return render(request, 'cms/media/index.html', {'title': 'Media', 'media': media})

# Render the add/edit media form or handle saving it
@login_required
def media_add_or_edit(request, id=False):
    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        # Pass the form all the HTTP POST data
        form = MediaForm(request.POST, request.FILES)

        # Run through any validation rules we have
        if form.is_valid():
            # Save the form data to the db
            form.save()

            # Show a success message to the user
            message_suffix = 'added!' if id is False else 'edited'
            messages.success(request, 'Media succesfully %s' % message_suffix)

            # Redirect them back to the media home page
            return redirect('media-home')

    # Were we passed the id? i.e are we editing an object, if so get it to pass to the template
    if id is not False:
        media = Media.objects.get(id=id)
        form = form if request.method == 'POST' else MediaForm(instance=media)
        template_data = {'form': form, 'title': media.title}

    # If not we must be adding new media as we have no id in the URL
    else:
        form = form if request.method == 'POST' else MediaForm()
        template_data = {'form': form, 'title': 'Add Media'}

    return render(request, 'cms/form.html', template_data)

@login_required
def media_view(request, id):
    media = Media.objects.get(id=id)

    return render(request, 'cms/media/view.html', {'media': media, 'title': media.title})

# Handles deleting a piece of media if the user is logged in
@login_required
def media_delete(request, id):
    # Look up the media object
    media = Media.objects.get(id=id)

    # Delete it from the database
    media.delete()

    # Show a success message to the user
    messages.success(request, 'Media succesfully deleted!')

    # Redirect them back to the media home page
    return redirect('media-home')

# Render the cms story home page if the user is logged in
@login_required
def story(request):
    return render(request, 'cms/index.html', {'title': 'Stories'})

# Render the cms user home page if the user is logged in
@login_required
def user(request):
    return render(request, 'cms/index.html', {'title': 'Users'})
