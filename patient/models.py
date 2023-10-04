from django.db import models
from django.contrib.auth.models import User
from doctor.models import *
# Create your models here.

class RegisterPatient(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=False,blank=False)
    name = models.CharField(max_length=100,null=False)
    phonenumber = models.CharField(max_length=10,null=False,unique=True)
    email = models.EmailField(blank=True,null=True)
    age = models.CharField(max_length=3,null=False)
    patientid = models.CharField(max_length=20)

    def __str__(self):
        return str(self.phonenumber + self.patientid)
    
class PatientsAppointment(models.Model):
    
    patient = models.ForeignKey(RegisterPatient,on_delete=models.CASCADE)
    doctor = models.ForeignKey(RegisterDoctor,on_delete=models.CASCADE)
    date = models.DateField(null = False)
