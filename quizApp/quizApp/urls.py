"""quizApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from quiz import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/',views.home,name='home'),
    path('quizPage/',views.quizPage,name='quizApp'),
    path('quizStart/',views.quizStart,name='quizStart'),
    path('quizSubmit/',views.quizSubmit,name='quizSubmit'),
    path('logout/',views.logout,name="logout"),
    path('report/',views.report,name='report'),
    path('summary/',views.summary,name='summary'),

    #admin
    path('adminHome/',views.adminHome,name="adminHome"),
    path('adminChoice/',views.adminChoice,name="adminChoice"),
    path('createQuiz/',views.createQuiz,name="createQuiz"),
    path('adminReport/',views.adminReport,name="adminReport"),
    path('studentReport/',views.studentReport,name="studentReport"),

    


]
