from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count

from api.models import CustomGroup, CustomGroupForm

# Render the cms group home page if the user is logged in
@login_required
def group(request):
    # Get the order_by param from the request
    order_by = request.GET.get('order_by', 'id')

    # Get the group
    groups = CustomGroup.objects.annotate(members=Count('user')).all().order_by(order_by)

    # List of fields to display in the template, passing this over
    # makes the template simpler
    fields = (
        {'name': 'id', 'title': 'ID'},
        {'name': 'name', 'title': 'Name'},
        {'name': 'members', 'title': 'Members'},
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

    return render(request, 'cms/group/index.html', {
        'title': 'Groups',
        'groups': groups,
        'fields': fields,
    })

# Render the add/edit media form or handle saving it
@login_required
def group_add_or_edit(request, id=False):
    user = request.user

    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        # If the id is not false then we are editing, so we need to
        # get an instance of that group first
        if id is not False:
            # Check the user has valid permissions to edit a group
            if user.has_perm('auth.wina_edit_group'):
                group = CustomGroup.objects.get(id=id)
                group_form = CustomGroupForm(request.POST, instance=group)

            else:
                raise PermissionDenied

        # Otherwise we can just pass the form data straight to the form, this is
        # a POST request for adding a group
        else:
            # Check the user has valid permissions to add a group
            if user.has_perm('auth.wina_add_group'):
                group_form = CustomGroupForm(request.POST)

            else:
                raise PermissionDenied

        # Run through any validation rules we have
        if group_form.is_valid():
            # Save the form data to the db
            group_form.save()

            # Show a success message to the group
            message_suffix = 'added!' if id is False else 'edited'
            messages.success(request, 'Group succesfully %s' % message_suffix)

            # Redirect them back to the group home page
            return redirect('group-home')

    # Were we passed the id? i.e are we editing an object, if so get it to pass to the template
    if id is not False:
        # Check the user has valid permissions to edit a group
        if user.has_perm('auth.wina_edit_group'):
            group = CustomGroup.objects.get(id=id)
            group_form = group_form if request.method == 'POST' else CustomGroupForm(instance=group)
            template_data = {'form': group_form, 'title': group.name}

        else:
            raise PermissionDenied

    # If not we must be adding new group as we have no id in the URL
    else:
        # Check the user has valid permissions to add a group
        if user.has_perm('auth.wina_add_group'):
            group_form = group_form if request.method == 'POST' else CustomGroupForm()
            template_data = {'form': group_form, 'title': 'Add Group'}

        else:
            raise PermissionDenied

    return render(request, 'cms/form.html', template_data)

# Handles retrieving a group object and returning it to the template
@login_required
def group_view(request, id):
    group = CustomGroup.objects.get(id=id)

    return render(request, 'cms/group/view.html', {'group': group, 'title': group.name})
