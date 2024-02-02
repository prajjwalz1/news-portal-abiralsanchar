from django.contrib import admin
from authentication_app.models import CustomUserModel
from django.contrib.auth.admin import UserAdmin

# Default 'User' model has be customized so,Explicitly define the new UserModel 
class CustomUserAdmin(UserAdmin):
 pass

admin.site.register(CustomUserModel,CustomUserAdmin)
