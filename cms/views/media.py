from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core import serializers

from api.models import Media, MediaForm
from modules.django_gcs_get_serving_url import get_serving_url

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
        # If the id is not false then we are editing, so we need to
        # get an instance of that media first
        if id is not False:
            media = Media.objects.get(id=id)
            media_form = MediaForm(request.POST, request.FILES, instance=media)

        # Otherwise we can just pass the form data straight to the form
        else:
            media_form = MediaForm(request.POST, request.FILES)

        # Run through any validation rules we have
        if media_form.is_valid():
            # Save the form data to the db
            form = media_form.save(commit=False)
            form.author = request.user
            form.content = get_serving_url(blob_key=request.FILES['file'].blob_key, file_name=request.FILES['file'].name)
            form.save()

            # Show a success message to the user
            message_suffix = 'added!' if id is False else 'edited'
            messages.success(request, 'Media succesfully %s' % message_suffix)

            # Redirect them back to the media home page
            return redirect('media-home')

    # Were we passed the id? i.e are we editing an object, if so get it to pass to the template
    if id is not False:
        media = Media.objects.get(id=id)
        media_form = media_form if request.method == 'POST' else MediaForm(instance=media)
        template_data = {'form': media_form, 'title': media.title}

    # If not we must be adding new media as we have no id in the URL
    else:
        media_form = media_form if request.method == 'POST' else MediaForm()
        template_data = {'form': media_form, 'title': 'Add Media'}

    return render(request, 'cms/form.html', template_data)

# Handles retrieving a media object and returning it to the template
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

# Handles searching Media and returning as JSON
def media_search_ajax(request, query):
    # Search for the object
    media = Media.objects.filter(title__icontains=query)

    # Serialize the data as json
    data = serializers.serialize('json', media)

    return HttpResponse(data, mimetype='application/json')

@login_required
def media_search_ui(request):
    return render(request, 'cms/media/search/ui.html', {'no_padding': True})
