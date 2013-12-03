from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from api.models import Media, MediaForm, CustomUser
from modules.django_gcs_get_serving_url import get_serving_url

# Render the cms media home page if the user is logged in
@login_required
def media(request):
    # Get the order_by param from the request
    order_by = request.GET.get('order_by', 'id')

    # Get the media
    media = Media.objects.all().order_by(order_by)

    # List of fields to display in the template, passing this over
    # makes the template simpler
    fields = (
        {'name': 'id', 'title': 'ID'},
        {'name': 'title', 'title': 'Title'},
        {'name': 'type', 'title': 'Type'},
        {'name': 'author', 'title': 'Author'},
        {'name': 'date_created', 'title': 'Date Created'},
    )

    # Loop the fields to add some extra data for the template
    for field in fields:
        # Is this the active field currently being sorted?
        if order_by.replace('-', '', 1) == field['name']:
            # If so add the direction arrow for if it's asc/desc
            field['arrow'] = '&darr;' if order_by[0:1] == '-' else '&uarr;'

            # Make the link the inverse of whatever the current sort direction is
            order_prefix = '' if order_by[0:1] == '-' else '-'
            field['link'] = request.path + '?order_by=' + order_prefix + field['name']

        # If not just add the link default to asc
        else:
            field['link'] = request.path + '?order_by=' + field['name']

    return render(request, 'cms/media/index.html', {
        'title': 'Media',
        'media': media,
        'fields': fields,
    })

# Render the add/edit media form or handle saving it
@login_required
def media_add_or_edit(request, id=False):
    user = request.user

    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        # If the id is not false then we are editing, so we need to
        # get an instance of that media first
        if id is not False:
            media = Media.objects.get(id=id)

            # Check the has valid permissions to edit this media
            if user.has_perm('api.wina_edit_any_media') or (media.author.id == user.id and user.has_perm('api.wina_edit_own_media')):
                media_form = MediaForm(request.POST, request.FILES, instance=media)

            else:
                raise PermissionDenied

        # Otherwise we can just pass the form data straight to the form, this is
        # a POST request for adding media
        else:
            # Check the user has valid permissions to add media
            if user.has_perm('api.wina_add_media'):
                media_form = MediaForm(request.POST, request.FILES)

            else:
                raise PermissionDenied

        # Run through any validation rules we have
        if media_form.is_valid():
            # Save the form data to the db
            media_form = media_form.save(commit=False)
            media_form.author = CustomUser.objects.get(id=request.user.id)

            # Is audio/video/image being submitted? If so we need to override content
            if media_form.type in ['audio', 'video', 'image']:
                media_form.content = get_serving_url(blob_key=request.FILES['file'].blob_key, file_name=request.FILES['file'].name)

            media_form.save()

            # Show a success message to the user
            message_suffix = 'added!' if id is False else 'edited'
            messages.success(request, 'Media succesfully %s' % message_suffix)

            # Redirect them back to the media home page
            return redirect('media-home')

    # Were we passed the id? i.e are we editing an object, if so get it to pass to the template
    if id is not False:
        media = Media.objects.get(id=id)

        # Check the user has valid permissions to edit this media
        if user.has_perm('api.wina_edit_any_media') or (media.author.id == user.id and user.has_perm('api.wina_edit_own_media')):
            media_form = media_form if request.method == 'POST' else MediaForm(instance=media)
            template_data = {'form': media_form, 'title': media.title}

        else:
            raise PermissionDenied

    # If not we must be adding new media as we have no id in the URL
    else:
        # Check the user has valid permissions to add a media
        if user.has_perm('api.wina_add_media'):
            media_form = media_form if request.method == 'POST' else MediaForm()
            template_data = {'form': media_form, 'title': 'Add Media'}

        else:
            raise PermissionDenied

    return render(request, 'cms/form.html', template_data)

# Handles retrieving a media object and returning it to the template
@login_required
def media_view(request, id):
    media = Media.objects.get(id=id)

    return render(request, 'cms/media/view.html', {'media': media, 'title': media.title})

# Handles deleting a piece of media if the user is logged in
@login_required
def media_delete(request, id):
    user = request.user

    # Look up the media object
    media = Media.objects.get(id=id)

    # Check the user has valid permissions to delete this story
    if user.has_perm('api.wina_delete_any_media') or (media.author.id == user.id and user.has_perm('api.wina_delete_own_media')):
        # Delete it from the database
        media.delete()

        # Show a success message to the user
        messages.success(request, 'Media succesfully deleted!')

        # Redirect them back to the media home page
        return redirect('media-home')

    else:
        raise PermissionDenied

@login_required
def media_search_tinymce(request):
    return render(request, 'cms/media/search/tinymce.html', {'no_padding': True})
