from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import *

routers = DefaultRouter()
routers.register(r'patient', RegisterPatientViewSet, basename='RegisterP')
routers.register(r'appointment',PatientsAppointmentDetails,basename='SetDoc')

urlpatterns = [
    
]

urlpatterns+= routers.urls