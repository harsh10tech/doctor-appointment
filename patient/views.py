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


class RegisterPatientViewSet(viewsets.ModelViewSet):
    Patient = RegisterPatient.objects.all()
    permission_classes = [AllowAny]

    @action(detail=False,methods=['POST'])
    def signup(self,request):

        data = request.data
        if data['phonenumber'] is None or data['first_name'] is None:
            return Response({"Error":"Both name and Licence number are required"}, 
                status = status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(username = data['phonenumber'])
        if user.exists():
            messages.error(request,'Username already exists !!')
            return Response(
                {"error":"username already registered !!"},
                status= status.HTTP_307_TEMPORARY_REDIRECT
            )
        
        user = User.objects.create(
            username = data['phonenumber'],
            first_name = data['first_name'],
            last_name = data['last_name']
        )
        user.set_password(data['password'])
        user.save()

        emailname = data['email'].split('@')[0]
        patientid = emailname+data['age']

        patient = self.Patient.create(
            user = user,
            name = data['first_name']+" "+data["last_name"],
            phonenumber = data['phonenumber'],
            email = data['email'],
            age = data['age'],
            patientid = patientid
        )
        patient.save()
        return Response({
            "message":"Successfully registered !!"
        },
        status = status.HTTP_202_ACCEPTED
        )
    
    @action(detail=False,methods=['POST'])
    def signin(self, request):

        data = request.data
        
        phonenumber = data['phonenumber']
        password = data['password']
        print(password)
        if not User.objects.filter(username=phonenumber).exists() or authenticate(username=phonenumber,password=password) is None:
            return Response(
                {"error":"Wrong username or Password"},400
            )
        else:
            user = authenticate(username=phonenumber,password=password)
            token,_ = Token.objects.get_or_create(user=user)
            login(request,user)

            return Response(
                {"success":"login successfull !!",
                 "token":token.key},202
            )
        
class PatientsAppointmentDetails(viewsets.ModelViewSet):

    month_dict = {1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"}
    
    month_num = int(date.today().month)

    @action(detail=False,methods=['GET'])
    def getdoctors(self,request):


        Doctors = RegisterDoctor.objects.all()
        # doc = DoctorSchedule.objects.select_related('doctor').all().values()
        docSchedule = DoctorSchedule.objects.all()
        # Create a dictionary with month numbers as keys and month names as values

        data = []
        for doctor in Doctors:
            schedule = docSchedule.get(doctor = doctor)
            # print(month)
            # schedule = json.dumps(schedule)
            monthly = MonthlyScheduleDoctor.objects.filter(doctor=doctor,month=self.month_dict[self.month_num])
            if monthly.exists():
                weekly = WeeklySchedule.objects.filter(monthly=monthly[0],appointment_on_week=schedule)
                data.append({
                    'doctor':{
                        'licence_number':doctor.licence_number,
                        'name':doctor.name,
                        'specialization':doctor.specialization,
                        'description':doctor.description,
                    },
                    'schedule':{
                        'location':schedule.location,
                        'day':schedule.day,
                        'start': schedule.start,
                        'end':schedule.end
                    },
                    'appointments':{week['date'].strftime("%d-%m-%Y"):week['appointments'] for week in weekly.values('date','appointments')}
                })

        return Response(data)

    @action(detail=False,methods=['POST'])
    def bookappointment(self,request):
        print(request.auth.user_id)
        data = request.data
        licence_number = data['licence_number']
        date = data['date']
        DATE_FORMAT = "%d-%m-%Y"
        date = datetime.strptime(date,DATE_FORMAT).date()
        print(date.month)
        user = User.objects.get(id=request.auth.user_id)
        patient = RegisterPatient.objects.get(user=user)
        doctor = RegisterDoctor.objects.get(licence_number=licence_number)
        monthly = MonthlyScheduleDoctor.objects.get(doctor=doctor,month = self.month_dict[int(date.month)])
        schedule = WeeklySchedule.objects.get(monthly=monthly,date =date)
        if schedule.appointments == 0:
            return Response("No appointment slots left, look for another day",202)
        schedule.appointments -= 1 
        schedule.save()
        
        patientappointment = PatientsAppointment.objects.filter(
            patient = patient,
            doctor = doctor,
            date = date
        )

        if patientappointment.exists():
            data = {"appointment allready booked on":patientappointment[0].date}
            return Response(data,202)
        else:
            patientappointment = PatientsAppointment.objects.create(
                patient = patient,
                doctor = doctor,
                date = date
            )
            patientappointment.save()



        return Response("Appointment Booked",202)
