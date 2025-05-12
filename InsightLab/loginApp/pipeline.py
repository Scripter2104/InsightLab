# # loginApp/pipeline.py
# import uuid
# from django.apps import apps
# from django.shortcuts import redirect
# from social_core.exceptions import AuthAlreadyAssociated
# from social_django.models import UserSocialAuth
#
# def safe_social_user(strategy, details, backend, uid, response, user=None, *args, **kwargs):
#     if user:
#         return {'social': None, 'user': user, 'is_new': False}
#
#     try:
#         social = UserSocialAuth.objects.select_related('user').get(
#             provider=backend.name,
#             uid=uid
#         )
#         return {'social': social, 'user': social.user, 'is_new': False}
#     except UserSocialAuth.DoesNotExist:
#         return {'social': None, 'user': None}
#     # any AuthAlreadyAssociated will just fall through and create_user will fire next
#
#
# def create_user(strategy, details, backend, uid, response, social=None, user=None, *args, **kwargs):
#     User = apps.get_model('auth', 'User')
#     # if social existed above, “user” is already set and is_new=False
#     if user:
#         return {'is_new': False, 'user': user}
#
#     base = details.get('username') or details.get('email').split('@')[0]
#     # guarantee unique usernames
#     username = f"{base}_{uuid.uuid4().hex[:6]}"
#     user = User.objects.create_user(
#         username=username,
#         email=details.get('email'),
#         password=None,
#     )
#     return {'is_new': True, 'user': user}
