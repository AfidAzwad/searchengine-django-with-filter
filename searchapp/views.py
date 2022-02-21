from datetime import date, timedelta
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
import requests
from bs4 import BeautifulSoup
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.db import models
from django.conf import settings
from django.views import View
from django.contrib import auth
from .models import *
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse


def home(request):
    query = ""
    keys = Search.group_by_counter()
    users = User.objects.filter(is_staff=False).order_by('id')
    # values_list() method returns a QuerySet containing tuples and flat=True will remove the tuples and return the list
    search = Search.objects.values_list('result', flat=True)
    if 'search' in request.GET:
        keys = Search.group_by_counter()
        users = User.objects.filter(is_staff=False)
        if request.user.is_authenticated:
            query = request.GET.get('search').strip().lower()
            result = requests.get('https://www.ask.com/web?q='+query)
            print(result)
            soup = BeautifulSoup(result.text, "html.parser")
            listing = soup.find_all(
                'div', {'class': 'PartialSearchResults-item'})
            search_result = []
            for result in listing:
                title = result.find(
                    class_='PartialSearchResults-item-title').text
                url = result.find('a').get('href')
                description = result.find(
                    class_='PartialSearchResults-item-abstract').text
                search_result.append((title, url, description))
            if search_result != []:
                if not Search.objects.filter(Q(keyword=query), Q(searched_by=request.user)).exists():
                    data = Search(keyword=query, searched_by=request.user,
                                  counter=1, result=search_result)
                    data.save()
                    diction = {'title': 'Google',
                               'search_result': search_result, 'keywords': keys, 'users': users}
                    return render(request, 'searchapp/home.html', context=diction)
                else:
                    Search.objects.filter(Q(keyword=query), Q(searched_by=request.user)).update(
                        counter=F("counter")+1, result=search_result)
                    diction = {'title': 'Google',
                               'search_result': search_result, 'keywords': keys, 'users': users}
                    return render(request, 'searchapp/home.html', context=diction)
            else:
                diction = {'title': 'Google', 'keywords': keys, 'users': users}
                return render(request, 'searchapp/home.html', context=diction)

        query = request.GET.get('search')
        # url = 'https://www.ask.com/web?q='+query
        result = requests.get('https://www.ask.com/web?q='+query)
        soup = BeautifulSoup(result.text, "html.parser")
        listing = soup.find_all(
            'div', {'class': 'PartialSearchResults-item'})
        search_result = []
        for result in listing:
            title = result.find(
                class_='PartialSearchResults-item-title').text
            url = result.find('a').get('href')
            description = result.find(
                class_='PartialSearchResults-item-abstract').text
            search_result.append((title, url, description))
        diction = {'title': 'Google', 'search_result': search_result,
                   'keywords': keys, 'users': users}
        return render(request, 'searchapp/home.html', context=diction)

    diction = {'title': 'Google', 'keywords': keys,
               'users': users, 'data': search}
    return render(request, 'searchapp/home.html', context=diction)


class LoginView(View):
    def get(self, request):
        return redirect('login')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                auth.login(request, user)
                return redirect(reverse('searchapp:home'))
            else:
                messages.error(
                    request, 'Invalid credentials,try again')
                return redirect('login')
        else:
            messages.error(
                request, 'Please fill all fields')
            return redirect('login')


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect(reverse('/'))


def filter_data(request):
    yesterday = date.today() - timedelta(days=1)
    last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
    start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
    keys = Search.group_by_counter()
    users = User.objects.filter(is_staff=False)
    keyword = request.GET.getlist('keyword[]')
    users = request.GET.getlist('user[]')
    time = request.GET.getlist('time[]')
    filterresult = Search.objects.values_list('result', flat=True)
    if len(keyword) > 0:
        filterresult = filterresult.values_list(
            'result', flat=True).filter(Q(keyword__in=keyword))
    if len(users) > 0:
        filterresult = filterresult.values_list(
            'result', flat=True).filter(Q(searched_by__username__in=users))
    if len(time) > 0:
        if '0' in time:
            filterresult = filterresult.values_list(
              'result', flat=True).filter(Q(searched_at__date=date.today()))
        if '1' in time:
            filterresult = filterresult.values_list(
              'result', flat=True).filter(Q(searched_at__date=yesterday))
        if '2' in time:
            filterresult = filterresult.values_list(
              'result', flat=True).filter(Q(searched_at__date__gte=date.today()-timedelta(days=7)),Q(searched_at__date__lt=datetime.today()))
        if '3' in time:
            filterresult = filterresult.values_list(
              'result', flat=True).filter(Q(searched_at__date__gte=start_day_of_prev_month),Q(searched_at__date__lte=last_day_of_prev_month)) 
            
    t = render_to_string('filter/home.html', {'data': filterresult})
    return JsonResponse({'data': t})
