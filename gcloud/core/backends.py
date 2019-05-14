# -*- coding: utf-8 -*-
from guardian.shortcuts import get_perms

from gcloud.core.models import Business


class GCloudPermissionBackend(object):

    def authenticate(self, username, password):
        """
        We do not authenticate user in this backend, so always return None.
        """
        return None

    def has_perm(self, user_obj, perm, obj=None):
        """
        If a user has manage_business perm for a exact business instance,
        he/she has all other perms of this business and related objects.
        """
        if isinstance(obj, Business):
            business = obj
        else:
            business = getattr(obj, 'business', None)

        if isinstance(business, Business) and \
                'manage_business' in get_perms(user_obj, business):
            return True
