from rest_framework import permissions

"""
class BlocklistPermission(permissions.BasePermission):

    #Global permission check for blocked IPs.


    def has_permission(self, request, view):
        ip_addr = request.META['REMOTE_ADDR']
        blocked = Blocklist.objects.filter(ip_addr=ip_addr).exists()
        return not blocked
"""

class APIAllowed(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        print(f'{user} tried to access the api with {user.groups.all()} groups.')
        if user.groups.filter(name='APIAllowed').exists():
            print('Permission Granted')
        else:
            print('Permission Denied')
        return user.groups.filter(name='APIAllowed').exists()