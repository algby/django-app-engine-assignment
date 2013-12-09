# Basic function to determine if the user is a staff member or not to
# decide whether to allow them access to the cms. This is separated out
# instead of just using a lambda to allow for more complex logic here in
# the future!
def can_access_cms(user):
    return user.is_staff or user.is_superuser
