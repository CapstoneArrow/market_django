from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from .models import User
from .forms import UpdateUserForm
import random
import string
from firebase_admin import db
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer


# 로그인
@api_view(['POST'])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response({'message': '로그인 되었습니다.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': '이메일 또는 비밀번호가 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)



# 로그아웃
@api_view(['POST'])
def logout_view(request):
    logout(request)
    return Response({'message': '로그아웃 되었습니다.'}, status=status.HTTP_200_OK)



# 회원가입
@api_view(['POST'])
def signup_view(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()

        # firebase
        ref = db.reference('users/'+user.username)
        ref.set({
            'username' : user.username,
            'password' : user.password,
            'email' : user.email
        })
        return Response({'message': '회원가입 되었습니다.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 아이디 찾기
@api_view(['POST'])
def find_username_view(request):
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)
        send_mail(
            '전통시장 아이디 찾기',
            f'가입된 아이디: {user.username}\n발신용 이메일 주소입니다.',
            'jeontong@sijang.com', # 표시되는 발송자 이메일 주소
            [email],
            fail_silently=False,
        )
        return Response({'message': '이메일로 아이디를 전송했습니다.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': '입력하신 정보를 다시 확인해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)


# 비밀번호 찾기
@api_view(['POST'])
def find_password_view(request):
    username = request.data.get("username")
    email = request.data.get("email")
    try:
        user = User.objects.get(username=username, email=email)
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user.password = make_password(temp_password)
        # 파이어베이스에 임시 비밀번호 저장
        ref = db.reference('users/'+user.username)
        ref.update({
            'password' : temp_password
        })
        user.set_password(temp_password)
        user.save()

        send_mail(
            '전통시장 임시 비밀번호 발급',
            f'임시 비밀번호(변경 권장): {temp_password}\n발신용 이메일 주소입니다.',
            'jeontong@sijang.com',  # 표시되는 발송자 이메일 주소
            [email],
            fail_silently=False,
        )
        return Response({'message': '이메일로 임시 비밀번호를 전송했습니다.'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'error': '입력하신 정보를 다시 확인해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)


# 회원정보 수정
@api_view(['POST', 'PUT'])
def update_profile_view(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.data, instance=request.user)
        if form.is_valid():
            if form.cleaned_data['new_password'] and form.cleaned_data['confirm_new_password']:
                request.user.set_password(form.cleaned_data['new_password'])

            if form.cleaned_data['username'] != request.user.username:
                request.user.username = form.cleaned_data['username']
            if form.cleaned_data['email'] != request.user.email:
                request.user.email = form.cleaned_data['email']

            request.user.save()

            # firebase
            ref = db.reference('users/'+request.user.username)
            ref.update({
                'username' : request.user.username,
                'password' : request.user.password,
                'email' : request.user.email
            })

            return Response({'message': '회원정보가 변경되었습니다.'}, status=status.HTTP_200_OK)
    else:
        form = UpdateUserForm(instance=request.user)

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': '회원정보가 변경되었습니다.'}, status=status.HTTP_200_OK)