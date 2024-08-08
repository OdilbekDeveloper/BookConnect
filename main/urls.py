from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import *


urlpatterns = [
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('auth/register/', User_Register),
    path('edit/user/', Edit_User),
    path('deactivate/user/', Deactivate_User),
    path('get/user/data/', Get_User_Data),


    path('book/add/', Add_Book),
    path('book/edit/<int:pk>/', Edit_Book),
    path('book/delete/<int:pk>/', Delete_Book),
]