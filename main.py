from flask import Flask, render_template, request, url_for, Markup
import urllib.request
from bs4 import BeautifulSoup as bs
from scipy import stats
import logging
import datetime
import os.path

app = Flask(__name__)

app.config["DEBUG"] = True

# constructor - load once (otherwise setup a local csv copy to save on bandwidth usage)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.logger.info(BASE_DIR)
'''
src = os.path.join(BASE_DIR, 'WHOSIS_000001,WHOSIS_000015.csv')
who_list = pd.read_csv(src)
who_list = who_list[['GHO (DISPLAY)', 'YEAR (CODE)' , 'COUNTRY (DISPLAY)', 'SEX (DISPLAY)', 'Numeric']]
who_list['COUNTRY (DISPLAY)'] = [ctry.title() for ctry in who_list['COUNTRY (DISPLAY)'].values]
country_list = sorted(set(who_list['COUNTRY (DISPLAY)'].values))
'''
def getPrice(country, car, model, year, distance, unit):
    page = urllib.request.urlopen('https://tradingeconomics.com/country-list/gasoline-prices').read()
    soup = bs(page,'html.parser')
    countriesA = soup.findAll("tr", {"class": "datatable-row"})
    countriesB = soup.findAll("tr", {"class": "datatable-row-alternating"})
    for countr in countriesA:
        children = countr.findAll("td" , recursive=False)
        td1 = children[0].text.replace("\r", "").replace("\n", "").strip()
        if td1 == country:
            price = float(children[1].text.replace("\r", "").replace("\n", "").strip())
            break
    for countr in countriesB:
        children = countr.findAll("td" , recursive=False)
        td1 = children[0].text.replace("\r", "").replace("\n", "").strip()
        if td1 == country:
            price = float(children[1].text.replace("\r", "").replace("\n", "").strip())
            break
    fuel = 'http://www.fuelly.com/car' +'/'+car+'/'+model
    search = year+" "+car+" "+model

    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = urllib.request.Request(fuel,headers=hdr)
    page = urllib.request.urlopen(req)
    soup = bs(page,'html.parser')
    
    mpg = float(soup.find("ul", {"title": search}).find("li",{"class": "summary-avg"}).find("span", {"class": "summary-avg-data"}).text)



    
    if unit == 'km':
        miles = distance*0.621
    else:
        miles = distance
    gallons = miles/mpg
    liters = gallons * 3.785
    
    total = round(price*liters, 2)
    
    return gallons, liters, total

@app.route('/', methods=['POST', 'GET'])
def interact():
    # select box defaults
    default_country = 'Select Country'
    selected_country = default_country
    default_car= 'Select Car'
    selected_car = default_car
    default_model = 'Select Model'
    selected_model = default_model
    default_year = 'Select year'
    selected_year = default_year
    default_distance= 'Select Distance'
    selected_distance = default_distance
    default_unit = 'Select Unit'
    selected_unit = default_unit

    # data carriers
    string_to_print = ''
    #healthy_image_list = []
    if request.method == 'POST':
        # clean up country field
        selected_country = request.form["country"]
        if (selected_country == default_country):
            selected_country = 'France'
        else:
            selected_country = selected_country
        # clean up car field
        selected_car = request.form["car"]
        if (selected_car == default_car):
            selected_car = 'Honda'
        # clean up model field
        selected_model = request.form["model"]
        if (selected_model == default_model):
            selected_model = 'Civic'
         # clean up year field
        selected_year = request.form["year"]
        if (selected_year == default_year):
            selected_year = '2019'
        else:
            selected_year = selected_year
        # clean up distance field
        selected_distance = request.form["distance"]
        if (selected_distance == default_distance):
            selected_distance = float(100)
        # clean up model field
        selected_unit = request.form["unit"]
        if (selected_unit == default_unit):
            selected_unit = 'km'


        # estimate mpg and price
        gallons, liters, total = getPrice(country=selected_country, car=selected_car, model=selected_model, year=selected_year, distance=float(selected_distance), unit=selected_unit)

        if (total is not None):
            # create output string
            string_to_print = Markup("This trip will cost you $ <font size='+10'>" + str(float(total)))
        else:
            string_to_print = Markup("Error! No data found for selected parameters")
            total = 1
        '''
        # healthy years
        healthy_image_list = []
        # squat.png, stretch.png, jog.png
        healthy_years_left = int(np.ceil(current_time_left))
        image_switch=0
        if (healthy_years_left > 0):
            for y in range(healthy_years_left):
                if image_switch == 0:
                    healthy_image_list.append('static/images/Cycling.png')
                elif image_switch == 1:
                    healthy_image_list.append('static/images/Jogging.png')
                elif image_switch == 2:
                    healthy_image_list.append('static/images/JumpingJack.png')
                elif image_switch == 3:
                    healthy_image_list.append('static/images/Stretching.png')
                elif image_switch == 4:
                    healthy_image_list.append('static/images/WeightLifting.png')
                else:
                    healthy_image_list.append('static/images/Yoga.png')
                    image_switch = -1
                image_switch += 1
        '''
    return render_template('total.html',
                            default_country = selected_country,
                            default_car=selected_car,
                            default_model =selected_model,
                            default_year = selected_year,
                            default_distance = selected_distance,
                            default_unit = selected_unit,
                            string_to_print = string_to_print)


# when running app locally
if __name__=='__main__':
    app.run(debug=True)
