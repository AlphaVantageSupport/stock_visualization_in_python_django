from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import StockData

import requests
import json

APIKEY = 'my_alphav_api_key'

DATABASE_ACCESS = True

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



