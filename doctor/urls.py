from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

routers = DefaultRouter()
routers.register(r'doctor', RegisterDoctorViewSet, basename='RegisterDOC')
routers.register(r'setdoc',DoctorOperation,basename='SetDoc')

urlpatterns = [
    
]

urlpatterns+= routers.urls