from django.contrib.auth.models import Group
from functools import wraps
from django.shortcuts import render

class CheckUserPermission:
    @staticmethod
    def check_role(user, group_names=None):
        """
        Check if the user is an administrator, superuser, or belongs to a list of specified groups.

        Administrators are like unit DP who can see all rooms.

        :param user: User object
        :param group_names: List of group names to check (defaults to ['Administrator', 'HRMC'] if not provided)
        :return: True if the user is in any of the provided groups or is a superuser, else False
        """
        try:
            # Default to checking for 'Administrator' and 'HRMC' groups if no other groups are provided
            if group_names is None:
                group_names = ['Administrator',]

            # Check if the user belongs to any of the groups in the list
            is_in_group = user.groups.filter(name__in=group_names).exists()
            is_superuser = user.is_superuser

            # Log group membership and superuser status for debugging purposes
            print(f'USER: {user} IS IN GROUPS {group_names}?: {is_in_group}, IS SUPERUSER?: {is_superuser}')

            # Return True if the user is in any of the specified groups or is a superuser
            return is_in_group or is_superuser
        except Exception as e:
            print(f"Error checking for administrators only: {e}")
            return False  # Return False if there's an error

    @staticmethod
    def role_required(group_names=None):
        """
        Check if the user belongs to the specified groups.
        """

        def decorator(view_func):
            @wraps(view_func)
            def _wrapped_view(request, *args, **kwargs):
                # Check if user is authenticated
                if not request.user.is_authenticated:
                    return render(request, 'authentication/page/page_403.html', status=403)

                # Ensure user is in the correct group(s)
                if not CheckUserPermission.check_role(request.user, group_names):
                    return render(request, 'authentication/page/page_403.html', status=403)

                return view_func(request, *args, **kwargs)

            return _wrapped_view

        return decorator
