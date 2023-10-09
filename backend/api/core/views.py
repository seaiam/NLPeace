from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from rest_framework import permissions
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer

from .forms import *

def signUp(request):  
    if request.method == 'POST':  
        form = UserRegistrationForm()  
        if form.is_valid():
            #user is saved to the database with info provided from the form  
            form.save()  
            return redirect('login.html')
    else:
        # empty form 
        form = UserRegistrationForm() 
    context = {  
        'form':form  
    }  
    return render(request, 'register.html', context)

def login(request):  
    if request.method == 'POST':  
        form = LogInForm()  
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if username is "":
                user = authenticate(request,email=email,password=password)
            else:
                user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                messages.success(request,f'logged in')
                return redirect('home.html')
        
        # form is not valid or user is not authenticated
        messages.error(request,f'Invalid username/email or password')
        return render(request,'login.html')
    else:
        # empty form 
        form = LogInForm() 
    context = {  
        'form':form  
    }  
    return render(request, 'login.html', context) 

def logout(request):
    logout(request)
    messages.success(request,f'logged out')
    return redirect('login.html')  

class UserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @staticmethod
    def get(request):
        user = User.objects.filter(uuid=request.user.uuid)
        serializer = UserSerializer(user)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_all():
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        if serializer.is_valid():
            return Response(serializer.data, status=status.HTTP_200_OK)
        Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def post(request):
        data = {
            'uuid': request.data.get('uuid'),
            'username': request.data.get('username'),
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
            'email': request.data.get('email'),
            'last_login': request.data.get('last_login'),
            'date_joined': request.data.get('date_joined'),
            'bio': request.data.get('bio'),
        }

        banner = request.data.get('banner')
        pic = request.data.get('pic')

        if banner:
            data['banner'] = banner
        if pic:
            data['pic'] = pic

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def put(request):
        user = User.objects.filter(uuid=request.user.uuid)
        if not user:
            return Response(
                {"res": "User with specified uuid does not exist"},
                status=status.HTTP_400_BAD_REQUEST
            )
        data = {
            'uuid': request.data.get('uuid'),
            'username': request.data.get('username'),
            'first_name': request.data.get('first_name'),
            'last_name': request.data.get('last_name'),
            'email': request.data.get('email'),
            'last_login': request.data.get('last_login'),
            'date_joined': request.data.get('date_joined'),
            'bio': request.data.get('bio'),
        }

        banner = request.data.get('banner')
        pic = request.data.get('pic')

        if banner:
            data['banner'] = banner
        if pic:
            data['pic'] = pic

        serializer = UserSerializer(instance=user, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def delete(request):
        user = User.objects.filter(uuid=request.user.uuid)
        # TODO verify that delete return type tuple<int, dict<str, int>> can be serialized by Response renderer
        return Response(user.delete(), status=status.HTTP_200_OK)
