from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core import serializers
from django.core.exceptions import PermissionDenied

from api.models import Story, StoryForm, CustomUser

# Render the cms story home page if the user is logged in
@login_required
def story(request):
    story = Story.objects.all()

    return render(request, 'cms/story/index.html', {'title': 'Stories', 'story': story})

# Render the add/edit media form or handle saving it
@login_required
def story_add_or_edit(request, id=False):
    user = request.user

    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        # If the id is not false then we are editing, so we need to
        # get an instance of that story first
        if id is not False:
            story = Story.objects.get(id=id)

            # Check the has valid permissions to edit this story
            if user.has_perm('api.wina_edit_any_story') or (story.author == user and user.has_perm('api.wina_edit_own_story')):
                # Get an instance of the StormForm
                story_form = StoryForm(request.POST, instance=story)

            else:
                raise PermissionDenied

        # Otherwise we can just pass the form data straight to the form, this is
        # a POST request for adding a story
        else:
            # Check the has valid permissions to add a story
            if user.has_perm('api.wina_add_story'):
                story_form = StoryForm(request.POST)

            else:
                raise PermissionDenied

        # Run through any validation rules we have
        if story_form.is_valid():
            # Save the form data to the db
            form = story_form.save(commit=False)
            user = CustomUser.objects.get(id=request.user.id)
            form.author = user
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

        # Check the has valid permissions to edit this story
        if user.has_perm('api.wina_edit_any_story') or (story.author == user and user.has_perm('api.wina_edit_own_story')):
            story_form = story_form if request.method == 'POST' else StoryForm(instance=story)
            template_data = {'form': story_form, 'title': story.title}

        else:
            raise PermissionDenied

    # If not we must be adding new story as we have no id in the URL
    else:
        # Check the has valid permissions to add a story
        if user.has_perm('api.wina_add_story'):
            story_form = story_form if request.method == 'POST' else StoryForm()
            template_data = {'form': story_form, 'title': 'Add Story'}

        else:
            raise PermissionDenied

    return render(request, 'cms/form.html', template_data)

# Handles retrieving a story object and returning it to the template
@login_required
def story_view(request, id):
    story = Story.objects.get(id=id)

    return render(request, 'cms/story/view.html', {'story': story, 'title': story.title})


# Handles deleting a piece of story if the user is logged in
@login_required
def story_delete(request, id):
    user = request.user

    # Look up the story object
    story = Story.objects.get(id=id)

    # Check the has valid permissions to delete this story
    if user.has_perm('api.wina_delete_any_story') or (story.author == user and user.has_perm('api.wina_delete_own_story')):
        # Delete it from the database
        story.delete()

        # Show a success message to the user
        messages.success(request, 'Story succesfully deleted!')

        # Redirect them back to the story home page
        return redirect('story-home')

    else:
        raise PermissionDenied

# Handles searching Story and returning as JSON
def story_search_ajax(request, query):
    # Search for the Story objects
    stories = Story.objects.filter(title__icontains=query)

    # Serialize the data as json
    data = serializers.serialize('json', stories)

    return HttpResponse(data, mimetype='application/json')
