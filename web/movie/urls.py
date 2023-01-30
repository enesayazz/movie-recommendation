from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.landing,name="landing"),
    path('sentiment', views.home, name="sentiment"),
    path('thinks',views.thinks,name="thinks"),
    path('movie',views.movie_recommend, name="movie"),
    path('movierec',views.movie_recommended, name="movierec"),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),

]
