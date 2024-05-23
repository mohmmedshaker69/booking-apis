from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrReadOnlyForAuthenticated(BasePermission):
 
 
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        if view.action in ['book', 'pay', 'rate']:
            return request.user.is_authenticated
        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        if view.action in ['book', 'pay', 'rate']:
            return request.user.is_authenticated
        return request.user.is_staff