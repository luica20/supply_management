# from django.shortcuts import redirect
# from django.contrib.auth.decorators import login_required
#
#
# def role_required(allowed_roles=[]):
#     def decorator(view_func):
#         @login_required
#         def wrapper(request, *args, **kwargs):
#             if request.user.is_authenticated and hasattr(request.user, 'customer'):
#                 role = request.user.customer.role
#             elif request.user.is_authenticated and hasattr(request.user, 'supplier'):
#                 role = request.user.supplier.role
#             else:
#                 role = None
#
#             if role in allowed_roles:
#                 return view_func(request, *args, **kwargs)
#             return redirect('home')  # Redirigir si no tiene el rol adecuado
#
#         return wrapper
#
#     return decorator