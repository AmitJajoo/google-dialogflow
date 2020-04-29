import smtplib
from flask import Flask, request, make_response,jsonify
from config_reader import ConfigReader
from email.mime.multipart import MIMEMultipart
import json
from email.message import EmailMessage
import requests as rq
from pydialogflow_fulfillment import DialogflowResponse, DialogflowRequest, SimpleResponse, Suggestions


app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():

    if request.method == "POST":
        req = request.get_json(silent=True, force=True)
        print(req)
        result = req.get("queryResult")
        intent = result.get("intent").get('displayName')
        if(intent == 'information'):
        	res = processRequest(req)
        	res = json.dumps(res, indent=4)
        	r = make_response(res)
        	r.headers['Content-Type'] = 'application/json'
        	return r
        elif(intent=='case'):
        	res = c(req)
        	dialogflow_response = DialogflowResponse(res)
        	dialogflow_response.add(SimpleResponse(res,res))
        	response = app.response_class(response=dialogflow_response.get_final_response(),mimetype='application/json')
        	return response

        elif(intent=='country_case'):
        	res = country(req)
        	dialogflow_response = DialogflowResponse(res)
        	dialogflow_response.add(SimpleResponse(res,res))
        	response = app.response_class(response=dialogflow_response.get_final_response(),mimetype='application/json')
        	return response

        elif(intent=='world'):

        	res = world(req)
        	dialogflow_response = DialogflowResponse(res)
        	dialogflow_response.add(SimpleResponse(res,res))
        	response = app.response_class(response=dialogflow_response.get_final_response(),mimetype='application/json')
        	return response

        elif(intent=='indiaStates'):

        	res = indiaSates(req)
        	dialogflow_response = DialogflowResponse(res)
        	dialogflow_response.add(SimpleResponse(res,res))
        	response = app.response_class(response=dialogflow_response.get_final_response(),mimetype='application/json')
        	return response

        elif(intent=="news"):
        	res = covid_news(req)
        	dialogflow_response = DialogflowResponse(res)
        	dialogflow_response.add(SimpleResponse(res,res))
        	response = app.response_class(response=dialogflow_response.get_final_response(),mimetype='application/json')
        	return response

        elif(intent=="menu"):
        	res = welcome(req)
        	dialogflow_response = DialogflowResponse(res)
        	dialogflow_response.add(SimpleResponse(res,res))
        	response = app.response_class(response=dialogflow_response.get_final_response(),mimetype='application/json')
        	return response

        elif(intent=="indiaCase"):
        	res = india(req)
        	dialogflow_response = DialogflowResponse(res)
        	dialogflow_response.add(SimpleResponse(res,res))
        	response = app.response_class(response=dialogflow_response.get_final_response(),mimetype='application/json')
        	return response

# case in india state
def indiaSates(req):
    sessionID = req.get('responseId')
    result = req.get("queryResult")
    user_says = result.get("queryText")
    parameters = result.get("parameters")
    state = parameters.get("geo-state")

    state = state.lower()
    state = state.title()
    if "&" in state:
        state = state.replace("&", "and")
    if state == "Tamilnadu":
        state = "Tamil Nadu"
    elif state == "Delhi ":
        state = "Delhi"
    try:

        url = "https://api.covid19india.org/data.json"

        response = rq.get(url)
        text = response.text
        stateWiseCases = json.loads(text)

        for i in range(0, 38):

            if stateWiseCases['statewise'][i]['state'] == state:
                # print(456)
                try:
                    confirmed = str(stateWiseCases['statewise'][i]["confirmed"])
                    print(confirmed)
                    active = str(stateWiseCases['statewise'][i]["active"])
                    print(active)
                    recovered = str(stateWiseCases['statewise'][i]["recovered"])
                    deaths = str(stateWiseCases['statewise'][i]["deaths"])
                    print(deaths+recovered)
                    fulfillmentText_one = state + " have Confirmed Cases: " + confirmed + "\nActive Cases: " + active + "\nRecovered Cases: " + recovered \
                                          + "\nDeaths: " + deaths
                    return fulfillmentText_one
                except Exception as e:
                    print(e)
        

    except Exception as e:
        print(e)

# email sending
def processRequest(req):

    config_reader = ConfigReader()
    configuration = config_reader.read_config()

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(configuration['SENDER_EMAIL'], configuration['PASSWORD'])
    print("login")

    sessionID = req.get('responseId')
    result = req.get("queryResult")
    user_says = result.get("queryText")
    parameters = result.get("parameters")
    cust_name = parameters.get("name")
    intent = result.get("intent").get('displayName')
    action = req.get('queryResult').get('action')
    print(action)
    if(intent == 'information'):   
        cust_contact = parameters.get("mobile")
        print(cust_contact)
        cust_email = parameters.get("email")
        print(cust_email)
        pin_code = parameters.get("pin_code")
        url = "https://api.postalpincode.in/pincode/"+str(pin_code)
        response = rq.get(url)
        test = response.text
        a = json.loads(test)
        try:
            district = a[0]['PostOffice'][0]['District']
            print(district)
            state = a[0]['PostOffice'][0]['State']
            print(state)
            country = a[0]['PostOffice'][0]['Country']
            print(country)
        except Exception as e:
            print(e)
        covid_case = "https://api.covid19india.org/state_district_wise.json"
        response_one = rq.get(covid_case)
        test_one = response_one.text
        a_one = json.loads(test_one)
        case = a_one[state]['districtData'][district]['confirmed']

        country_link = "https://corona.lmao.ninja/v2/countries"
        response_country = rq.get(country_link)
        test_country = response_country.text
        a_country = json.loads(test_country)
        print(len(a_country))

        total = a_country[92]['cases']
        
        active_case = a_country[92]['active']
        death = a_country[92]['deaths']

        subject = 'Covid-19 precaution and case'
        me="Total Case in India {}\nActive Case in India {}\nTotal Deaths in India {}\n".format(total,active_case,death)
        me_one="There are {} cases in {}\n\nTo prevent the spread of COVID-19:\n".format(case,district)

        point_one="1.Clean your hands often. Use soap and water, or an alcohol-based hand rub.\n"
        
        
        point_two="2.Maintain a safe distance from anyone who is coughing or sneezing.\n"
        point_three="3.Don’t touch your eyes, nose or mouth.\n"
        point_four="4.Cover your nose and mouth with your bent elbow or a tissue when you cough or sneeze.\n"
        point_five="5.Stay home if you feel unwell.\n"
        point_six="6.If you have a fever, a cough and difficulty breathing, seek medical attention. Call in advance.\n"
        point_seven="7.Follow the directions of your local health authority."
        m=me+me_one+point_one+point_two+point_four+point_five+point_six+point_seven
  
        message_one = 'Subject: {}\n\n{}'.format(subject, m)
        
        try:

        	server.sendmail(configuration['SENDER_EMAIL'], cust_email, message_one)
        except Exception as e:
        	print("E-mail is not valid")
       
        print("Email has been sent to ", cust_email)
        server.quit()

# for city case
def c(req):
    print("hi")
    sessionID = req.get('responseId')
    result = req.get("queryResult")
    user_says = result.get("queryText")
    parameters = result.get("parameters")
    geo_city=parameters.get('geo-city')

    url="https://api.covid19india.org/state_district_wise.json"


    response=rq.get(url)
    text=response.text
    a=json.loads(text)

    for i in a:
        for j in a[i]['districtData']:
            if j==geo_city:
                state=i
                case_covid=a[state]['districtData'][geo_city]['confirmed']
                active_case=a[state]['districtData'][geo_city]['active']
                total_information="Total case:"+str(case_covid)+"\n"+"Active Case:"+str(active_case)
                return total_information
#country case
def country(req):
    sessionID = req.get('responseId')
    result = req.get("queryResult")
    user_says = result.get("queryText")
    parameters = result.get("parameters")
    geo_country=parameters.get('geo-country')
    print(geo_country)
    url = "https://corona.lmao.ninja/v2/countries/"+geo_country
    response=rq.get(url)
    text=response.text
    a=json.loads(text)

    case=a['cases']
    active=a['active']
    death=a['deaths']

    total_information_two=geo_country+" has total case :"+str(case)+"\n"+"Active Case :"+str(active)+"\n"+"Total Deaths :"+str(death)
    print(total_information_two)

    return total_information_two
#india case
def india(req):
    url = "https://corona.lmao.ninja/v2/countries/india"
    response=rq.get(url)
    text=response.text
    a=json.loads(text)

    case=a['cases']
    active=a['active']
    death=a['deaths']

    total_information_two="Total Case :"+str(case)+"\n"+"Active Case :"+str(active)+"\n"+"Total Deaths :"+str(death)
    print(total_information_two)

    return total_information_two

def world(req):
	
    url = "https://coronavirus-19-api.herokuapp.com/all"
    response=rq.get(url)
    text=response.text
    a=json.loads(text)

    case=a['cases']
    recovered=a['recovered']
    death=a['deaths']
    total_information="Total Case :"+str(case)+"\n"+"Recovered Case :"+str(recovered)+"\n"+"Total Deaths :"+str(death)
    print(total_information)

    return total_information



def covid_news(req):
    config_reader = ConfigReader()
    configuration = config_reader.read_config()
    news=[]
    url = "http://newsapi.org/v2/top-headlines?country=in&category=health&apiKey="+configuration['NEWS']
    response=rq.get(url)
    text=response.text
    a=json.loads(text)


    for i in range(20):
	    title=a['articles'][i]['title']
	    author=a['articles'][i]['author']
	    news_feed=str(i+1)+". "+str(title)+" - "+str(author)
	    news.append(news_feed)
    fulfillmentText_two="\n".join(news)
    return fulfillmentText_two

#menu that occur in telegram
def welcome(req):
	instructions="1./aboutcorona - Know about corona virus\n2./symptoms - Symptoms of COVID-19\n3./precautions - Precautions needed for COVID-19.\n4./news - Reports COVID-19 india cases.\n5./indiacases - Reports COVID-19 India case.\n6./indiacity - Report COVID-19 City case.\n7./state_case - Reports state wise COVID-19 cases.\n8./globalcase - Reports COVID-19 Global cases\n9./countrycases - Reports country wise COVID-19 cases.\n10./covidmap - Displays global map country wise COVID-19 cases.\n11./quarantinetips - Tips for what you can do in quarantine.\n12./mythbuster - Some myths about COVID-19."
	return instructions

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)
    app.run(debug=True) # running the app 

