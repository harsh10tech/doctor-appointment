from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class RegisterDoctor(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=False,blank=False)
    name = models.CharField(max_length=100,null=False)
    licence_number = models.CharField(max_length=10,null=False,unique=True)
    email = models.EmailField(blank=True,null=True)
    phonenumber = models.CharField(max_length=10,null=True,blank=True)
    specialization = models.CharField(max_length = 100,null=False)
    description = models.TextField()

    def __str__(self):
        return self.licence_number + self.name + self.specialization
    
class DoctorSchedule(models.Model):

    doctor = models.OneToOneField(RegisterDoctor,on_delete=models.CASCADE)
    location = models.CharField(max_length=100,null=False)
    DAYS = [
        ("Monday","MON"),
        ("Tuesday","TUE"),
        ("Wednesday","WED"),
        ("Thursday","THU"),
        ("Friday","FRI"),
        ("Saturday","SAT")
    ]
    day = models.CharField(max_length=9,choices=DAYS)
    duration = models.CharField(max_length=2)
    start = models.TimeField()
    end = models.TimeField()

class MonthlyScheduleDoctor(models.Model):

    MONTHS = [("JAN","January"),("FEB","February"), ("MAR","March"), 
              ("APR","April"), ("MAY","May"),("JUN","June"), 
              ("JUL","July"),("AUG","August"),("SEP","September"),
               ("OCT","October"),("NOV","November"), ("DEC","December")]
    doctor = models.ForeignKey(RegisterDoctor,on_delete=models.CASCADE)
    month = models.CharField(max_length=15,choices=MONTHS)

    class Meta:
        constraints =[
            models.UniqueConstraint(fields=['doctor','month'],name='monthly')
        ]

class WeeklySchedule(models.Model):

    monthly  = models.ForeignKey(MonthlyScheduleDoctor,on_delete=models.CASCADE)
    appointment_on_week = models.ForeignKey(DoctorSchedule,on_delete=models.CASCADE)
    date = models.DateField()
    appointments = models.IntegerField(default=0)

