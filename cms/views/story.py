from django.shortcuts import redirect, render
from django.contrib.auth.decorators import user_passes_test
from cms.helpers import can_access_cms
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from api.models import Story, StoryForm, WinaUser

# Render the cms story home page if the user is logged in
@user_passes_test(can_access_cms)
def story(request):
    # Get the order_by param from the request
    order_by = request.GET.get('order_by', 'id')

    # Get the story
    story = Story.objects.all().order_by(order_by)

    # List of fields to display in the template, passing this over
    # makes the template simpler
    fields = (
        {'name': 'id', 'title': 'ID'},
        {'name': 'title', 'title': 'Title'},
        {'name': 'author', 'title': 'Author'},
        {'name': 'status', 'title': 'Status'},
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

    return render(request, 'cms/story/index.html', {
        'title': 'Story',
        'story': story,
        'fields': fields,
    })

# Render the add/edit media form or handle saving it
@user_passes_test(can_access_cms)
def story_add_or_edit(request, id=False):
    user = request.user

    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        # If the id is not false then we are editing, so we need to
        # get an instance of that story first
        if id is not False:
            story = Story.objects.get(id=id)

            # Check the user has valid permissions to edit this story
            if user.has_perm('api.wina_edit_any_story') or (story.author.id == user.id and user.has_perm('api.wina_edit_own_story')):
                # Get an instance of the StormForm
                story_form = StoryForm(request.POST, instance=story, user=user)

            else:
                raise PermissionDenied

        # Otherwise we can just pass the form data straight to the form, this is
        # a POST request for adding a story
        else:
            # Check the user has valid permissions to add a story
            if user.has_perm('api.wina_add_story'):
                story_form = StoryForm(request.POST, user=user)

            else:
                raise PermissionDenied

        # Run through any validation rules we have
        if story_form.is_valid():
            # Save the form data to the db
            form = story_form.save(commit=False)
            form.author = WinaUser.objects.get(id=request.user.id)
            form.save()

            # Show a success message to the user
            message_suffix = 'added!' if id is False else 'edited'
            messages.success(request, 'Story succesfully %s' % message_suffix)

            # Redirect them back to the story home page
            return redirect('story-home')

    # Were we passed the id and it wasn't a POST request?
    # i.e are we editing an object, if so get it to pass to the template
    if id is not False:
        story = Story.objects.get(id=id)

        # Check the user has valid permissions to edit this story
        if user.has_perm('api.wina_edit_any_story') or (story.author.id == user.id and user.has_perm('api.wina_edit_own_story')):
            story_form = story_form if request.method == 'POST' else StoryForm(instance=story, user=user)
            template_data = {'form': story_form, 'title': story.title}

        else:
            raise PermissionDenied

    # If not we must be adding new story as we have no id in the URL
    else:
        # Check the user has valid permissions to add a story
        if user.has_perm('api.wina_add_story'):
            story_form = story_form if request.method == 'POST' else StoryForm(user=user)
            template_data = {'form': story_form, 'title': 'Add Story'}

        else:
            raise PermissionDenied

    return render(request, 'cms/form.html', template_data)

# Handles retrieving a story object and returning it to the template
@user_passes_test(can_access_cms)
def story_view(request, id):
    story = Story.objects.get(id=id)

    return render(request, 'cms/story/view.html', {'story': story, 'title': story.title})


# Handles deleting a piece of story if the user is logged in
@user_passes_test(can_access_cms)
def story_delete(request, id):
    user = request.user

    # Look up the story object
    story = Story.objects.get(id=id)

    # Check the user has valid permissions to delete this story
    if user.has_perm('api.wina_delete_any_story') or (story.author.id == user.id and user.has_perm('api.wina_delete_own_story')):
        # Delete it from the database
        story.delete()

        # Show a success message to the user
        messages.success(request, 'Story succesfully deleted!')

        # Redirect them back to the story home page
        return redirect('story-home')

    else:
        raise PermissionDenied
