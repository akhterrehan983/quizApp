from tkinter.messagebox import QUESTION
from urllib import response
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import requests
from django.contrib import messages
from collections import OrderedDict 
from django.template.defaulttags import register

@csrf_exempt 
def home(request):    
    if "emailorusername" in request.session:
        response = requests.get("http://127.0.0.1:5000/getQuiz")
        data = response.json()
        for obj in data:
            obj["id"] = obj["_id"]["$oid"]
            del obj["_id"]
        return render(request,"home.html",{"quizList":data})
    if request.method=="POST":
        name = request.POST.get("buttonName")
        if name == "signUp":
            email = request.POST.get("email")
            username = request.POST.get("username")
            password = request.POST.get("password")
            body = {"username":username,"email":email,"password":password}
            response = requests.post(url = "http://127.0.0.1:5000/studentRegister", json = body)
            if response.status_code == 200:
                messages.success(request, 'User added successfully!!!')
            else:
                messages.error(request, response.json()["error"])
                return render(request,"loginRegister.html")
        elif name == "login":
            emailOrUsername = request.POST.get("emailOrUsername")
            password = request.POST.get("password")
            response1 = requests.post(url = "http://127.0.0.1:5000/studentLogin", json = {"email":emailOrUsername,"password":password})
            response2 = requests.post(url = "http://127.0.0.1:5000/studentLogin", json = {"username":emailOrUsername,"password":password})
            response = None 
            if response1.status_code == 200:
                response = response1
            elif response2.status_code == 200:
                response = response2
            if response and response.status_code == 200:
                request.session['emailorusername'] = response.json()["username"]
                response = requests.get("http://127.0.0.1:5000/getQuiz")
                data = response.json()
                for obj in data:
                    obj["id"] = obj["_id"]["$oid"]
                    del obj["_id"]
                return render(request,"home.html",{"quizList":data})
            else:
                messages.error(request, "Invalid Credentials!!!")
    return render(request,"loginRegister.html")
    
def quizPage(request):
    if "emailorusername" in request.session:
        return render(request,"home.html")
    else:
        return render(request,"loginRegister.html")


@csrf_exempt
def quizStart(request):
    if "emailorusername" in request.session:
        if request.method == "POST":
            quizId = request.POST.get("quizId")
            response = requests.get("http://127.0.0.1:5000/getQuizById/"+quizId).json()
            return render(request,"quizPage.html",{
                "questions":response["questions"],
                "quizId":response["_id"]["$oid"],
                "quizName":response["quizName"],
                "duration":response["duration"]})
        return render(request,"home.html")
    else:
        return render(request,"loginRegister.html")

@csrf_exempt
def quizSubmit(request):
    questions = {}
    for i in range(100):
        if request.POST.get(str(i)) != None:
            question = request.POST.get("question"+str(i))
            ans = int(request.POST.get(str(i)))
            questions[question] = ans
    username = request.session["emailorusername"]
    quizId = request.POST.get("quizId")
    response = requests.post("http://127.0.0.1:5000/addReport/"+username+"/"+quizId,json=questions)
    response = response.json()
    return redirect('/home/') 


def logout(request):
    if "emailorusername" in request.session:
        del request.session['emailorusername']
    return redirect('/home/') 



#report
def report(request,username=None):
    if username!=None or "emailorusername" in request.session:
        if username == None:
            username = request.session["emailorusername"]
        response = requests.get("http://127.0.0.1:5000/getReportByusername/"+username)
        response = response.json()
        data = {}
        for quizId,value in response["response"].items():
            resp = requests.get("http://127.0.0.1:5000/getQuizById/"+quizId).json()
            data[quizId] = [resp["quizName"],resp["duration"]]
            l = []
            for i in value:
                x = 0
                for ind in i:
                    if ind == "dateTime":
                        continue
                    if i[ind] == resp["questions"][ind][-1]:
                        x+=1
                l.append(x)
            x = 0
            d = {}
            for i in value:
                d[x] = [str(l[x])+"/"+str(len(resp["questions"])),i["dateTime"]]
                x+=1
            data[quizId].append(dict(reversed(list(d.items()))))
        data = OrderedDict(sorted(data.items()))
        return render(request,"report.html",{"data":data})
    else:
        return redirect('/home/') 


@csrf_exempt
def summary(request):
    quizId,ind = request.POST.get("id").split("&nbsp")
    username = request.session["emailorusername"]
    response = requests.get("http://127.0.0.1:5000/getReportByusernameQuizId/"+username+"/"+quizId).json()[int(ind)]
    questions = requests.get("http://127.0.0.1:5000/getQuizById/"+quizId).json()["questions"]
    result = []
    for question in questions:
        c = response.get(question,None)
        questions[question].append(c)
    
    return render(request,"summary.html",{"questions":questions})

@register.filter
def to_char(value):
    return chr(96+value)

@register.filter
def to_charCap(value):
    return chr(64+value)


#admin
def adminHome(request):
    return render(request,"admin/adminHome.html")

def adminChoice(request):
    choice = request.POST.get("choice")
    if choice=="createQuiz":
        return render(request,"admin/createQuiz.html")
    elif choice=="quizReport":
        return adminReport(request)
    else:
        redirect("adminHome")


@csrf_exempt 
def createQuiz(request):
    if request.method == "POST":
        quizName = request.POST.get("quizName")
        duration = request.POST.get("duration")

        body = {"quizName":quizName,"duration":int(duration)}
        questions = {}
        for i in range(1,101,1):
            if request.POST.get("q"+str(i),None) == None:
                continue
            questions[request.POST.get("q"+str(i),None)] = [
                request.POST.get("a"+str(i),None),
                request.POST.get("b"+str(i),None),
                request.POST.get("c"+str(i),None),
                request.POST.get("d"+str(i),None),
                int(request.POST.get("ans"+str(i),None))
            ]

        body["questions"] = questions
        response = requests.post("http://127.0.0.1:5000/addQuiz",json=body)
        if response.status_code == 409:
            messages.error(request, response.json()["error"])
    return render(request,"admin/adminHome.html")

def adminReport(request):
    response = requests.get("http://127.0.0.1:5000/getStudent").json()
    return render(request,"admin/report.html",{"data":response})

def studentReport(request):
    username = request.POST.get("username")
    return report(request,username)
    