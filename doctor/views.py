from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import action
from rest_framework import viewsets,status
from .models import *
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated,AllowAny
from datetime import date, datetime,time

class RegisterDoctorViewSet(viewsets.ModelViewSet):

    Doctor = RegisterDoctor.objects.all()
    permission_classes = [AllowAny]

    @action(detail=False,methods=['POST'])
    def signup(self,request):

        data = request.data
        if data['licence_number'] is None or data['first_name'] is None:
            return Response({"Error":"Both name and Licence number are required"}, 
                status = status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(username = data['licence_number'])
        if user.exists():
            user.delete()
            messages.error(request,'Username already exists !!')
            return Response(
                {"error":"username already registered !!"},
                status= status.HTTP_307_TEMPORARY_REDIRECT
            )
        
        user = User.objects.create(
            first_name = data['first_name'],
            last_name = data['last_name'],
            username = data['licence_number']
        )
        user.set_password(data['password'])
        user.save()
        doctor = self.Doctor.create(
            user = user,
            licence_number = data['licence_number'],
            name = data['first_name'] + " "+ data['last_name'],
            email = data['email'],
            phonenumber = data['phonenumber'],
            specialization = data['specialization'],
            description = data['description']
        )
        doctor.save()
        return Response({
            "message":"Successfully registered !!"
        },
        status = status.HTTP_202_ACCEPTED
        )
    
    @action(detail=False,methods=['POST'])
    def signin(self, request):

        data = request.data
        
        licence_number = data['licence_number']
        password = data['password']


        if not User.objects.filter(username=licence_number).exists() or authenticate(username=licence_number,password=password) is None:
            return Response(
                {"error":"Wrong username or Password"},400
            )
        else:
            print(licence_number,password)
            user = authenticate(username=licence_number,password=password)
            token,_ = Token.objects.get_or_create(user=user)
            login(request,user)

            return Response(
                {"success":"login successfull !!",
                 "token":token.key},202
            )
        

class DoctorOperation(viewsets.ModelViewSet):
    doctorSchedule = DoctorSchedule()

    @action(detail=False,methods=['POST'])
    def setschedule(self,request):

        data = request.data

        user = User.objects.get(id=request.auth.user_id)
        location = data['location']
        day = data['day']
        duration = data['duration']
        start = data['start']
        end = data['end']
        appointments = data['appointments']
        month = data['month']
        date = data['date']

        DATE_FORMAT = "%d-%m-%Y"
        TIME_FORMAT = "%I:%M %p"

        date = datetime.strptime(date,DATE_FORMAT).date()
        start = datetime.strptime(start,TIME_FORMAT).time()
        end = datetime.strptime(end,TIME_FORMAT).time()
                                 
        print(user.first_name,location,day,duration,start,end,appointments)

        doctor = RegisterDoctor.objects.get(user = user)
        
        obj = DoctorSchedule.objects.filter(doctor=doctor)
        if not obj.exists():
            query= DoctorSchedule.objects.create(
                doctor = doctor,
                location = location,
                day = day,
                duration = duration,
                start = start,
                end = end,
            )
            print(user.first_name,location,day,duration,start,end,appointments)

            query.save()
        else:
            query = DoctorSchedule.objects.filter(doctor=doctor).update(
                location = location,
                day = day,
                duration = duration,
                start = start,
                end = end
            )
        print(user.first_name,location,day,duration,start,end,appointments)
        query = DoctorSchedule.objects.get(doctor=doctor)

        if not MonthlyScheduleDoctor.objects.filter(doctor=doctor,month=month).exists():
            Monthly = MonthlyScheduleDoctor.objects.create(
                doctor = doctor,
                month = month
            )
            Monthly.save()
        print(user.first_name,location,day,duration,start,end,appointments)

        Monthly = MonthlyScheduleDoctor.objects.get(doctor = doctor,month=month)
        
        schedule = WeeklySchedule.objects.create(
            monthly = Monthly,
            appointment_on_week = query,
            date = date,
            appointments = appointments
        )
        schedule.save()
        
        return Response(202)