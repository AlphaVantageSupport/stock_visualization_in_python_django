# Building a Stock Visualization Website with Python/Django and Alpha Vantage APIs

## Installing Dependencies 
This web application has been tested on Python 3.6 or higher. 

Dependencies: 
- Django: `pip install django`
- requests: `pip install requests`

Alpha Vantage API key


Command line
```shell
(home) $ django-admin startproject alphaVantage
```

folder structure: 
```
alphaVantage/
    alphaVantage/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
    manage.py
```

Go from your home directory to the project directory
```shell
(home) $ cd alphaVantage
```

create the stock visualizer app: 
```shell
(alphaVantage) $ python manage.py startapp stockVisualizer
```

create the HTML file for our homepage: 
```shell
(alphaVantage) $ mkdir templates
```
```shell
(alphaVantage) $ cd templates
```
```shell
(templates) $ touch home.html
```
```shell
(templates) $ cd ../
``` 

Empty home.html

folder structure: 
```
alphaVantage/
    alphaVantage/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
    stockVisualizer/
        migrations/
            __init__.py
        __init__.py
        admin.py
        apps.py
        models.py
        tests.py
        views.py
    templates/
        home.html
    manage.py
```

Update settings.py (CNS)
at the top of the script:
```python
from pathlib import Path
import os #add this line
```

Inside the `INSTALLED_APPS`
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'stockVisualizer', #add this line
]
```

Inside `TEMPLATES`, register the template folder we just created
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], #modify this line
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```




## Specify the database model
```python
#models.py

from django.db import models

# Create your models here.
class StockData(models.Model):
    symbol = models.TextField(null=True)
    data = models.TextField(null=True)
```

Register the data model to the database 
```shell
(alphaVantage) $ python manage.py makemigrations
```
```shell
(alphaVantage) $ python manage.py migrate
```

Folder structure: 
```
alphaVantage/
    alphaVantage/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
    stockVisualizer/
        migrations/
            0001_initial.py #you should see this after running the database migration commands
            __init__.py
        __init__.py
        admin.py
        apps.py
        models.py
        tests.py
        views.py
    templates/
        home.html
    manage.py
    db.sqlite3 #you should see this after running the database migration commands
```

## Set up the homepage 
home.html
```html
<!DOCTYPE html>
<html>
<head>
    <!--<link rel="stylesheet" href="style.css">-->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.2.1/dist/chart.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <title>Stock Visualizer</title>
</head>

<body>
<h2>Interative Stock Visualizer</h2>
<br>

<label for="ticker-input">Enter Symbol:</label>
<input type="text" id="ticker-input">
<input type="button" value="submit" id="submit-btn">
<br>

<div id="graph-area" style="height:80%; width:80%;">
<canvas id="myChart"></canvas>
</div>
<br>

<div>
    Friendly reminder: if the graphing function stops working after several successful instances, don't worry! It is likely that you have reached the 5 requests/minute rate limit of the free Alpha Vantage API key. The graph should work again in the next minute or after you obtain a <a href="https://www.alphavantage.co/premium/" target="_blank">premium API key</a> with a higher rate limit.
</div>

<script>

    $(document).ready(function(){
        // Right after the page is loaded, we get the stock data (default to AAPL) from the Django backend (the 'get_stock_data' function) for plotting
        $.ajax({
              type: "POST",
              url: "/get_stock_data/",
              data: {
                 'ticker': 'AAPL',
              },
              success: function (res, status) {
                var tickerDisplay = res['prices']['Meta Data']['2. Symbol'];
                var graphTitle = tickerDisplay + ' (data for the trailing 500 trading days)'

                var priceSeries = res['prices']['Time Series (Daily)'];
                var daily_adjusted_close = [];
                var dates = [];

                price_data_parse = function(){
                    for (let key in priceSeries) {
                        daily_adjusted_close.push(Number(priceSeries[key]['5. adjusted close']));
                        dates.push(String(key));
                    }

                };
                price_data_parse();

                var smaSeries = res['sma']['Technical Analysis: SMA'];
                var sma_data = [];

                sma_data_parse = function(){
                    for (let key in smaSeries) {
                        sma_data.push(Number(smaSeries[key]['SMA']));
                    }

                };
                sma_data_parse();



                daily_adjusted_close.reverse().slice(500);
                sma_data.reverse().slice(500);
                dates.reverse().slice(500);

                //make a graph
                var ctx = document.getElementById('myChart').getContext('2d');
                var myChart = new Chart(ctx, {
                type: 'line',
                    data: {
                        labels: dates.slice(-500),
                        datasets: [
                            {
                                label: 'Daily Adjusted Close',
                                data: daily_adjusted_close.slice(-500),
                                backgroundColor: [
                                    'green',
                                ],
                                borderColor: [
                                    'green',
                                ],
                                borderWidth: 1
                            },
                            {
                                label: 'Simple Moving Average (SMA)',
                                data: sma_data.slice(-500),
                                backgroundColor: [
                                    'blue',
                                ],
                                borderColor: [
                                    'blue',
                                ],
                                borderWidth: 1
                            },
                        ]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                //beginAtZero: false
                            }
                        },
                        plugins: {
                            legend: {
                            position: 'top',
                            },
                            title: {
                            display: true,
                            text: graphTitle
                            }
                        }
                    }
                });

              }
        });
    });

    $('#submit-btn').click(function() {
        // when the user specifies a new ticker, we call the Django backend (the 'get_stock_data' function) to get the stock data and refresh the graph. 
        var tickerText = $('#ticker-input').val();
        $.ajax({
              type: "POST",
              url: "/get_stock_data/",
              data: {
                 'ticker': tickerText,
              },
              success: function (res, status) {
                var tickerDisplay = res['prices']['Meta Data']['2. Symbol'];
                var graphTitle = tickerDisplay + ' (data for the trailing 500 trading days)'

                var priceSeries = res['prices']['Time Series (Daily)'];
                var daily_adjusted_close = [];
                var dates = [];

                price_data_parse = function(){
                    for (let key in priceSeries) {
                        daily_adjusted_close.push(Number(priceSeries[key]['5. adjusted close']));
                        dates.push(String(key));
                    }

                };
                price_data_parse();

                var smaSeries = res['sma']['Technical Analysis: SMA'];
                var sma_data = [];

                sma_data_parse = function(){
                    for (let key in smaSeries) {
                        sma_data.push(Number(smaSeries[key]['SMA']));
                    }

                };
                sma_data_parse();



                daily_adjusted_close.reverse().slice(500);
                sma_data.reverse().slice(500);
                dates.reverse().slice(500);

                //make a graph
                $('#myChart').remove(); // this is my <canvas> element
                $('#graph-area').append('<canvas id="myChart"><canvas>');
                var ctx = document.getElementById('myChart').getContext('2d');
                var myChart = new Chart(ctx, {
                type: 'line',
                    data: {
                        labels: dates.slice(-500),
                        datasets: [
                            {
                                label: 'Daily Adjusted Close',
                                data: daily_adjusted_close.slice(-500),
                                backgroundColor: [
                                    'green',
                                ],
                                borderColor: [
                                    'green',
                                ],
                                borderWidth: 1
                            },
                            {
                                label: 'Simple Moving Average (SMA)',
                                data: sma_data.slice(-500),
                                backgroundColor: [
                                    'blue',
                                ],
                                borderColor: [
                                    'blue',
                                ],
                                borderWidth: 1
                            },
                        ]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                //beginAtZero: false
                            }
                        },
                        plugins: {
                            legend: {
                            position: 'top',
                            },
                            title: {
                            display: true,
                            text: graphTitle
                            }
                        }
                    }
                });

              }
        });


    });

</script>

</body>
</html>
```

## Set up Django backend
views.py
```python
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import StockData

import requests
import json

APIKEY = 'my_alphav_api_key' #replace 'my_alphav_api_key' with your actual Alpha Vantage API key obtained at https://www.alphavantage.co/support/#api-key

DATABASE_ACCESS = True #if False, the app will always query the Alpha Vantage APIs regardless of whether the stock data is already in the database

# Create your views here.
def home(request):
    return render(request, 'home.html', {})

@csrf_exempt
def get_stock_data(request):
    if request.is_ajax():
        ticker = request.POST.get('ticker', 'null')
        ticker = ticker.upper()

        if DATABASE_ACCESS == True:
            if StockData.objects.filter(symbol=ticker).exists(): 
                #checking if the database already has data stored for this ticker before querying the Alpha Vantage API
                entry = StockData.objects.filter(symbol=ticker)[0]
                return HttpResponse(entry.data, content_type='application/json')

        output_dictionary = {}

        price_series = requests.get(f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={ticker}&apikey={APIKEY}&outputsize=full').json()
        sma_series = requests.get(f'https://www.alphavantage.co/query?function=SMA&symbol={ticker}&interval=daily&time_period=10&series_type=close&apikey={APIKEY}').json()

        output_dictionary['prices'] = price_series
        output_dictionary['sma'] = sma_series

        temp = StockData(symbol=ticker, data=json.dumps(output_dictionary))
        temp.save()

        return HttpResponse(json.dumps(output_dictionary), content_type='application/json')

    else:
        message = "Not Ajax"
        return HttpResponse(message)
```

## URL routing
urls.py
```python
"""alphaVantage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
import stockVisualizer.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", stockVisualizer.views.home),
    path('get_stock_data/', stockVisualizer.views.get_stock_data),
]
```

## Running the website locally
```shell
(alphaVantage) $ python manage.py runserver
```


You should have a fully functional Django web application at http://localhost:8000/

## References




