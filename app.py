from __future__ import print_function
from flask import Flask, abort, render_template, request
from configparser import ConfigParser

from os import path
import os
from news_scrapper import scrapper

# import json to load JSON data to a python dictionary
import json

# urllib.request to make a request to api
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import urllib

from flask import make_response
import requests


app = Flask(__name__)

ICONS = path.join("static", "icons")


app.config['UPLOAD_FOLDER'] = ICONS



@app.route("/")
def index():
    return render_template("home.html")

@app.route("/weather", methods=["GET", "POST"])
def weather():
    if request.method == "POST":
        city = request.form['city']
        city = city.replace(' ', '+')
    else:
        city = 'lagos'
    api = '48a09fb347f5f6bd562f1f58287eda4f'
    try:
        source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q='+city + '&appid=' + api).read()
        forecast = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast?q='+city + '&appid=' + api).read()
    except:
        city = 'lagos'

        source = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/weather?q='+city + '&appid=' + api).read()
        list_of_data = json.loads(source)
        data = {
		"country_code": str(list_of_data['sys']['country']),
		"coordinate": str(list_of_data['coord']['lon']) + ' '
					+ str(list_of_data['coord']['lat']),
		# "temp": str(list_of_data['main']['temp']) + 'k',
		"pressure": str(list_of_data['main']['pressure']),
		"humidity": str(list_of_data['main']['humidity']),
        "cityname": city.replace('+', ' '),
        "temp_cel": str(round(list_of_data['main']['temp']-273.15,2)),
        "temp_max_cel": str(round(list_of_data['main']['temp_max']-273.15,2)),
        "temp_min_cel": str(round(list_of_data['main']['temp_min']-273.15,2)),
        "desc": list_of_data['weather'][0]['description'],
        'icon': list_of_data['weather'][0]['icon'],
        'wind_speed': str(list_of_data['wind']['speed']),
	}
        # 5 days Forecast
        forecast = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast?q='+city + '&appid=' + api).read()
        days_forecast = json.loads(forecast)
        forecast_data = days_forecast["list"][:4]

        return render_template('weather.html', msg='City name invalid!', data=data, forecast_data=forecast_data)
    list_of_data = json.loads(source)
    data = {
		"country_code": str(list_of_data['sys']['country']),
		"coordinate": str(list_of_data['coord']['lon']) + ' '
					+ str(list_of_data['coord']['lat']),
		# "temp": str(list_of_data['main']['temp']) + 'k',
		"pressure": str(list_of_data['main']['pressure']),
		"humidity": str(list_of_data['main']['humidity']),
        "cityname": city.replace('+', ' '),
        "temp_cel": str(round(list_of_data['main']['temp']-273.15,2)),
        "temp_max_cel": str(round(list_of_data['main']['temp_max']-273.15,2)),
        "temp_min_cel": str(round(list_of_data['main']['temp_min']-273.15,2)),
        "desc": list_of_data['weather'][0]['description'],
        'icon': list_of_data['weather'][0]['icon'],
        'wind_speed': str(list_of_data['wind']['speed']),
	}
    # 5 days Forecast
    forecast = urllib.request.urlopen('http://api.openweathermap.org/data/2.5/forecast?q='+city + '&appid=' + api).read()
    days_forecast = json.loads(forecast)
    forecast_data = days_forecast["list"][:4]

    print(forecast_data)

    return render_template('weather.html', data = data, forecast_data=forecast_data)


# news route
@app.route('/wayg-news', methods=['GET'])
def news():
    titles,article_links,article_img_links,news_contents=scrapper()

    return render_template('news.html',titles=titles,article_links=article_links,article_img_links=article_img_links,news_contents=news_contents)



# getting coordinated to be passed as args in the forecast api
def get_latitude_longitude(city):
    try:
        city_url = 'https://api.openweathermap.org/geo/1.0/direct'
        url_params = {
            'APPID': weather_api,
            'q': city
        }
        coordinates = requests.get(url=city_url, params=url_params)
        codJson = coordinates.json()

        result = [codJson[0]['lat'], codJson[0]['lon']]
    except:
        abort(400, "Error Handling Data")

    return result

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    #return 'hello'
    # print(f"Req: {req}")


    res = processRequest(req)

    # print(res)
    return res


def processRequest(req):
    if req.get("queryResult").get("action") != "weather":
        return {}
    baseurl = "http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=48a09fb347f5f6bd562f1f58287eda4f"
    yql_query,city = makeYqlQuery(req)
    if yql_query is None:
        return {}
    r = requests.get(baseurl.format(city)).json()

    res = makeWebhookResult(r,city)
    return res


def makeYqlQuery(req):
    #print(req)
    req=req.get("queryResult")
    parameters = req.get("parameters")
    # print(parameters)
    result = parameters.get("address")
    print("---------")
    print(f"result: {result}")

    #result=result[0]
    city=result['city']

    #print(result.get('city'))
   # parameters = result.get("parameters")
    #city = result.get("city")
    if city is None:
        return None
    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')",city


def makeWebhookResult(data,city):
   main1=data['weather'][0]
   main2=data['main']
   celsius=(main2['temp']-32)*0.5555
   celsius=truncate(celsius,2)
   #print(type(main2['temp']))
   speech = "Today the weather in " + city + " is " + main1['description'] + \
              ", And today's temperature is " + str(celsius) + "^" + 'C'
   return {
        "fulfillmentText": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }
def truncate(num, n):
    integer = int(num * (10**n))/(10**n)
    return float(integer)

@app.route('/test', methods=['GET'])
def test():
    return  "Hello there my friend !!"

@app.route('/static_reply', methods=['POST'])
def static_reply():
    speech = "Hello there, this reply is from the webhook !! "
    my_result =  {
        "speech": speech,
        "displayText": speech,
    }
    res = json.dumps(my_result, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r




if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')