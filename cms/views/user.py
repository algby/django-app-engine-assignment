from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from cms.helpers import can_access_cms
from django.core.exceptions import PermissionDenied
from api.models import WinaUser, CmsUserForm, WinaGroup

# Render the cms user home page if the user is logged in
@user_passes_test(can_access_cms)
def user(request):
    # Get the order_by param from the request
    order_by = request.GET.get('order_by', 'id')

    # Get the user
    users = WinaUser.objects.all().order_by(order_by)

    # List of fields to display in the template, passing this over
    # makes the template simpler
    fields = (
        {'name': 'id', 'title': 'ID'},
        {'name': 'username', 'title': 'Username'},
        {'name': 'first_name', 'title': 'First Name'},
        {'name': 'last_name', 'title': 'Last Name'},
        {'name': 'email', 'title': 'Email'},
        {'name': 'Groups', 'title': 'Groups', 'sortable': False},
        {'name': 'date_joined', 'title': 'Date Joined'},
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

    return render(request, 'cms/user/index.html', {
        'title': 'Users',
        'users': users,
        'fields': fields,
    })

# Render the add/edit user form or handle saving it
@user_passes_test(can_access_cms)
def user_add_or_edit(request, id=False):
    current_user = request.user

    # Is it a POST request, i.e is the form being submitted
    if request.method == 'POST':
        # If the id is not false then we are editing, so we need to
        # get an instance of that user first
        if id is not False:
            user = WinaUser.objects.get(id=id)

            # Check the has valid permissions to edit this user
            if current_user.has_perm('auth.wina_edit_any_user') or (current_user.id == user.id and current_user.has_perm('auth.wina_edit_own_user')):
                user_form = CmsUserForm(request.POST, instance=user)

            else:
                raise PermissionDenied

        # Otherwise we can just pass the form data straight to the form, this is
        # a POST request for adding user
        else:
            # Check the user has valid permissions to add user
            if current_user.has_perm('auth.wina_add_user'):
                user_form = CmsUserForm(request.POST)

            else:
                raise PermissionDenied

        # Run through any validation rules we have
        if user_form.is_valid():
            # Save the form data to the db
            user = user_form.save()

            # Was a group set for the user?
            group_ids = request.POST.getlist('groups', False)

            # Clear the users existing group memberships, this isn't optimal
            # but it works well enough
            user.groups.clear()

            # If so add the user to that group
            if group_ids:
                for group_id in group_ids:
                    user.groups.add(WinaGroup.objects.get(id=group_id))

            # Show a success message to the user
            message_suffix = 'added!' if id is False else 'edited'
            messages.success(request, 'User succesfully %s' % message_suffix)

            # Redirect them back to the user home page
            return redirect('user-home')

    # Were we passed the id? i.e are we editing an object, if so get it to pass to the template
    if id is not False:
        user = WinaUser.objects.get(id=id)

        # Check the user has valid permissions to edit this user
        if current_user.has_perm('auth.wina_edit_any_user') or (current_user.id == user.id and current_user.has_perm('auth.wina_edit_own_user')):
            user_form = user_form if request.method == 'POST' else CmsUserForm(instance=user)
            template_data = {'form': user_form, 'title': user.first_name + ' ' + user.last_name}

        else:
            raise PermissionDenied

    # If not we must be adding new user as we have no id in the URL
    else:
        # Check the user has valid permissions to add a user
        if current_user.has_perm('auth.wina_add_user'):
            user_form = user_form if request.method == 'POST' else CmsUserForm()
            template_data = {'form': user_form, 'title': 'Add User'}

        else:
            raise PermissionDenied

    return render(request, 'cms/form.html', template_data)

# Handles retrieving a user object and returning it to the template
@user_passes_test(can_access_cms)
def user_view(request, id):
    user = WinaUser.objects.get(id=id)

    return render(request, 'cms/user/view.html', {'user': user, 'title': user.first_name + ' ' + user.last_name})

# Handles activating another user if the current user is logged in
@user_passes_test(can_access_cms)
def user_activate(request, id):
    # Look up the user object and get the current user
    user = WinaUser.objects.get(id=id)
    current_user = request.user

    # Check the user has valid permissions to delete this story
    if current_user.has_perm('auth.wina_activate_any_user'):
        # Activate the user
        user.is_active = True
        user.save()

        # Show a success message to the user
        messages.success(request, 'User succesfully activated!')

        # Redirect them back to the user home page
        return redirect('user-home')

    else:
        raise PermissionDenied

# Handles deactivating another user if the current user is logged in
@user_passes_test(can_access_cms)
def user_deactivate(request, id):
    # Look up the user object and get the current user
    user = WinaUser.objects.get(id=id)
    current_user = request.user

    # Check the user has valid permissions to delete this story
    if current_user.has_perm('auth.wina_activate_any_user'):
        # Deactive the user
        user.is_active = False
        user.save()

        # Show a success message to the user
        messages.success(request, 'User succesfully deactivated!')

        # Redirect them back to the user home page
        return redirect('user-home')

    else:
        raise PermissionDenied
