from django.shortcuts import render,redirect
from .forms import CreateUserForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .decorators import unauthenticated_user
from .models import Account,Meet,MeetParticipant
from django.contrib.auth.decorators import login_required
import plotly.figure_factory as ff
import plotly
import datetime
from django.contrib import messages
from datetimerange import DateTimeRange
from django.contrib.auth.models import User
from django.core.mail import send_mail

# Create your views here.


def index(request):
    return redirect('login')


@unauthenticated_user
def loginPage(request):
    if request.user.is_authenticated:
            return redirect('dashboard')
    else:
        if request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('dashboard')
            else:
                messages.info(request,'Kullanıcı Adı veya Şifre yanlış')
        return render(request,"login.html")

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                user = form.save()
                
                messages.success(request,'Kayıt Başarılı')
                return redirect('login')
    context = {'form':form}
    return render(request,'register.html',context)


def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    accountInfo = Account.objects.get(user=request.user)

    meets = Meet.objects.filter(creater_account=accountInfo).values()
    time = meets.values('id','title','start_date','finish_date')
    result = []
    for t in time:
        meetDict =	{
            "id": "id",
            "title": "title",
            "start_date": "start_date",
            "finish_date":"finish_date"
            }
        meet_date = t.get('start_date')
        meet_date = str(meet_date)[:10]
        meet_id = t.get('id')
        meet_title = t.get('title')
        finish_date = t.get('finish_date')

        meetDict.update({"id":meet_id})
        meetDict.update({"title":meet_title})
        meetDict.update({"start_date":meet_date})
        meetDict.update({"finish_date":finish_date})
        result.append(meetDict)


    today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
    

    members = MeetParticipant.objects.filter(participant_id = request.user.id).values()
    test = members.values_list('meet_id')
    todayDict = {
        "Task" : "Task",
        "Start": "Start",
        "Finish" : "Finish"
    }
    todayData = []
    for i in test:
        i = str(i).replace("(","")
        i = i.replace(",)","")
        
        data = Meet.objects.filter(id=i,start_date__range=(today_min, today_max)).values('title','start_date','finish_date')
        title = str(data.values('title')).replace("<QuerySet [{'title': '","")
        title = title.replace("'}]>","")
        start = str(data.values('start_date'))
        start = start.replace("<QuerySet [{'start_date': datetime.datetime(","")
        start_hours = start.replace(", tzinfo=<UTC>)}]>","")[12:16].replace(",",":").strip()
        start_minutes = start.replace(", tzinfo=<UTC>)}]>","")[16:19].strip()
        finish = str(data.values('finish_date'))
        finish = finish.replace("<QuerySet [{'finish_date': datetime.datetime(","")
        finish_hours = finish.replace(", tzinfo=<UTC>)}]>","")[12:16].replace(",",":").strip()
        finish_minutes = finish.replace(", tzinfo=<UTC>)}]>","")[16:19].strip()
        
        
        
        todayDict.update({"Task":title})
        todayDict.update({"Start":start_hours+start_minutes})
        todayDict.update({"Finish":finish_hours+finish_minutes})
        todayData.append(dict(todayDict))


    figDict = {
        "Task" : "Task",
        "Start": "Start",
        "Finish" : "Finish"
    }
    figData = []
    for r in result:
        figDict.update({"Task":r.get('title')})
        figDict.update({"Start":r.get('start_date')})
        figDict.update({"Finish":r.get('finish_date')})
        figData.append(dict(figDict))

    fig = ff.create_gantt(figData)
    
    scriptfile =plotly.offline.plot(fig, output_type="div", show_link=False, link_text=False)
    

    if request.method == 'POST':
        startDate = request.POST['meet-date-start'] +"T" +request.POST['meet-time-start'] + "+0900"
        finishDate = request.POST['meet-date-finish']+ "T" + request.POST['meet-time-finish'] +"+0900"
        timeRangeGet = DateTimeRange(startDate,finishDate)
        test = True
        for t in meets:
            meet_date = t.get('start_date')
            finish_date = t.get('finish_date')
            timeRangeData = DateTimeRange(meet_date,finish_date)
            control = timeRangeData in timeRangeGet
            if control == True:
                test = False
                break
                
        if test == True:
            meet_create = Meet.objects.create(
                creater_account = accountInfo,
                title = request.POST["title"],
                meet_links = request.POST["meet_links"],
                meet_location = request.POST["meet_location"],
                start_date = startDate,
                finish_date = finishDate ,
                summary = request.POST["summary"],
            )
            meet_create.save()
            return redirect('meetDetails', title=request.POST["title"])
        else:
            messages.error(request, 'Aynı Saatte Toplantınız Bulunmakta')

    context = {'accountInfo':accountInfo,'meets':result,'scriptfile':scriptfile,"today_meet":todayData}



    return render(request,"dashboard.html",context)

@login_required(login_url='login')
def meetDetails(request,title):
    accountInfo = Account.objects.get(user=request.user)
    meets = Meet.objects.filter(title=title).values()
    meeting = Meet.objects.get(title=title)
    new_members = []
    new_members_dict = {'username':'username'}
    members = []
    accounts = User.objects.all().values('username')
    

    for member in meeting.get_participant():
        members.append(member)
    
    for account in accounts:
        account = str(account).replace("{'username': '","").replace("'}","")
        new_members.append(account)

    test = []
    return_list = []
    for added_member in members:
        replace_str = title + "-"
        added_member = str(added_member).replace(replace_str,"")
        test.append(added_member)

    unregisteredList = (set(new_members) - set(test))
    for unregistered in unregisteredList:
        if unregistered != 'admin':
            new_members_dict.update({'username':unregistered})
            return_list.append(dict(new_members_dict)) 
    
   

    if request.method == 'POST':
        addMembers = MeetParticipant.objects.create(
            meet = meeting,
            participant = User.objects.get(username = request.POST['new_member']),
        )
        addMembers.save()
        messages = str(request.user) + "tarafından " + str(meets.get('title')) + "başlıklı toplantıya eklendiniz."+"Toplantı" +str(meets.get('start_date'))+"/"+str(meets.get('finish_date'))+ "Tarihleri arasındadır."
        email = User.objects.filter(id=request.POST['new_member']).values('email')
        send_mail("Toplantı Hatırlatma",messages,"brainsforce@gmail.com",[email],fail_silently=False)
        return redirect(request.META['HTTP_REFERER'])
    
    context = {'accountInfo':accountInfo,'meets':meets,'members':members,'new_members':return_list}
    return render(request,"meets.html",context)



