from django.shortcuts import render


# Create your views here.
def home(request):
    return render(request, 'home.html')


def register(request):
    return render(request, 'register.html')


def register_complete(request):
    # 인증 메일 보내기
    print(request.method)
    print(request.POST.get('nickname'))
    # 완료 페이지 띄우기
    return render(request, 'register_complete.html')
