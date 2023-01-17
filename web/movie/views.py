from base64 import urlsafe_b64decode,urlsafe_b64encode
from email.message import EmailMessage
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site  
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
import numpy as np
from . tokens import generate_token
import nltk
from django.http import JsonResponse
from . import forms
import pandas as pd
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
movlist=[]
def mr ():
    
        df=pd.read_csv('final.csv')

        movie_mat=pd.pivot_table(df,values='rating',index='title',columns='userId').fillna(0)
        movie_mat_new=movie_mat.reset_index()

        from scipy.sparse import csr_matrix
        vec_movie_mat=csr_matrix(movie_mat.values)

        from sklearn.neighbors import NearestNeighbors
        knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
        knn.fit(vec_movie_mat)

        
        movie_mat_new[movie_mat_new['title']=='Matrix, The (1999)']

        x=movie_mat.iloc[5512,:].values.reshape(1,-1)

        distance,indices= knn.kneighbors(x, n_neighbors = 10)
        lst=[]
        for i in range(len(distance.flatten())):
            lst.append(movie_mat.index[indices.flatten()][i])#,distance.flatten()[i])
        for e in lst:
            movlist.append(e)
        movliste = movlist[1:11]
        print(movliste)


def home (request):
    context = {"a":"1/10"}
    return render(request,"movie/index.html",context)

def thinks(request):
    if request.method == "POST":
        thinkval= request.POST.get("thinkval")
    
       
        text = thinkval
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        print(f'Overall sentiment: {scores}')
        pos = scores.get('pos')
        neg = scores.get('neg')
        neu = scores.get('neu')
        list = [pos,neg,neu]
        if max(list) == pos:
            com = "You liked it"
        elif max(list) == neg:
            com = "you did not like it"
        else:
            com = "you are neutural or don't know it"
        

    
    context = {"b":com,"a":"2/10"}
    return render(request,"movie/index.html",context)



def movie_recommend(request):

    if request.method == "POST":
        filmval = request.POST.get("filmval")

        
    return render (request,"movie/movie.html")

def movie_recommended(request):
    if request.method == "POST":
        filmval = request.POST.get("filmval")
        
        df=pd.read_csv('final.csv')

        movie_mat=pd.pivot_table(df,values='rating',index='title',columns='userId').fillna(0)
        movie_mat_new=movie_mat.reset_index()

        from scipy.sparse import csr_matrix
        vec_movie_mat=csr_matrix(movie_mat.values)

        from sklearn.neighbors import NearestNeighbors
        knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
        knn.fit(vec_movie_mat)

        
        movie_mat_new[movie_mat_new['title']=="Screamers (1995)"]

        x=movie_mat.iloc[5512,:].values.reshape(1,-1)

        distance,indices= knn.kneighbors(x, n_neighbors = 10)
        lst=[]
        for i in range(len(distance.flatten())):
            lst.append(movie_mat.index[indices.flatten()][i])#,distance.flatten()[i])
        for e in lst:
            movlist.append(e)
        movliste = movlist[1:11]
        
            
    
    context={"c":filmval,"d":movliste,"i":i}
    
    return render (request,"movie/recommend.html",context)
    


def signup (request,):

    if request.method == "POST":
        username = request.POST.get("username")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        pass1 = request.POST.get("pass1")
        pass2 = request.POST.get("pass2")

        if User.objects.filter(username=username):
            messages.error(request,"username already exist")
            return redirect("signup")

        if User.objects.filter(email=email):
            messages.error(request,"email already exist")
            return redirect("signup")

        if pass1 != pass2:
            messages.error(request,"passwords did not match")
        

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False 
        myuser.save()

        messages.error(request, "your account has been created")

        #welcome email

        subject = " welcome to movie recommender"
        message = " hello " + myuser.first_name + "!! \n" + "welcome to the site "
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject,message,from_email,to_list, fail_silently = True)
        # return redirect('signin')

        # Email Confirmation
        current_site = get_current_site(request)
        email_subject = "Confirm your email"
        message2= render_to_string("movie/email_confirmation.html",{'name':myuser.first_name,
                                                             'domain': current_site.domain,
                                                             'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
                                                             'token': generate_token.make_token(myuser)})
        
        # email = EmailMessage(
        #     email_subject,
        #     message2,settings.EMAIL_HOST_USER,
        #     [myuser.email]
        # )
        send_mail(email_subject,message2,from_email,to_list,fail_silently=True)
        messages.success(request, f'Dear {myuser.first_name}, please go to your email and click on activation link.')
    
        # email.fail_silently = True
        # email.send()
        

    return render(request, "movie/signup.html")

def signin (request):

    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')
         
        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name   
            return render(request, "movie/index.html",{'fname':fname})

        else:
            messages.error(request, "Username Or Password Wrong !")
            return redirect('signin')
    
    return render(request, "movie/signin.html")

def signout (request):
    logout(request)
    messages.success(request, "logged out")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        # login(request, myuser)
        messages.success(request, "Thank you for your email confirmation. Now you can use your account.")
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')



def activateEmail(request, myuser, to_list):
    mail_sub = "Activate your user account"
    mess= render_to_string("movie/email_confirmation.html",{'name':myuser.first_name,
                                                            'domain': get_current_site(request).domain,
                                                            'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
                                                            'token': generate_token.make_token(myuser),
                                                            "protocol":'https'if request.is_secure() else 'http'})
    mail = EmailMessage(mail_sub,mess,to=[to_list])



def my_view(request):
    form = forms.MyForm(request.POST)
    if form.is_valid():
        my_field_value = form.cleaned_data['my_field']
        # Do something with the form data here
        # ...
        return render(request, 'index.html', {'form': form, 'my_field_value': my_field_value})
    else:
        return render(request, 'index.html', {'form': form})