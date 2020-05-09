from rest_framework import permissions
from user import models


class AccessPolicyException(Exception):
    pass


class ZstAccessPolicy(permissions.BasePermission):

    def has_permission(self, request, view):
        # 获取当前view的action
        action = self._get_invoked_action(view)
        permission_name = self._get_invoked_permission(view)
        try:
            p = models.Permission.objects.get(name=permission_name)
        except models.Permission.DoesNotExist:
            raise AccessPolicyException("no permission found")
        action = models.ActionSet.objects.filter(permission__pk=p.pk, action=action).first()
        if action is None:
            raise AccessPolicyException("no action found")

        user = request.user
        print(user)
        action_set = set(user.actions.values_list("id", flat=True))
        for role in user.roles.all():
            action_set = action_set.union(set(role.actions.values_list("id", flat=True)))

        if action.id in action_set:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return super().has_object_permission(request, view, obj)

    def _get_invoked_action(self, view) -> str:
        """
            If a CBV, the name of the method. If a regular function view,
            the name of the function.
        """
        if hasattr(view, "action"):
            return view.action
        elif hasattr(view, "__class__"):
            return view.__class__.__name__
        raise AccessPolicyException("Could not determine action of request")

    def _get_invoked_permission(self, view) -> str:
        if hasattr(view, "permission_name"):
            return view.permission_name
        elif hasattr(view, "__class__"):
            return view.__class__.__name__
        raise AccessPolicyException("Could not determine permission name of request")
