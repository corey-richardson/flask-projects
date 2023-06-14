# Flask Imports
from flask import Flask, render_template, request, redirect, url_for
from forms import GetScoreData
# Pandas - dataframe management
import pandas as pd
# Datetime - used to get todays date
from datetime import date
# Auto-open web browser to page
import webbrowser

PATH = "static/scores.csv"

# Flask setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# event = input("Event Name: ")
# TEST LINE, UNCOMMENT INPUT ABOVE IN RELEASE BUILD
event = "Plympton Lamb Feast"

today = date.today().strftime("%d/%m/%Y")
@app.context_processor
def set_event():
    return dict(event_name=event, date=today)

webbrowser.open("http://127.0.0.1:5000/")

# "Index" Route / Homepage
# Read and process data from csv file
# Sort by highest score and convert to a list
# Display in table format using template "index.html"
@app.route('/', methods=["GET","POST"])
def index():
    score_data = pd.read_csv(PATH)
    score_data = score_data.sort_values(by=["score"], ascending=False)
    score_data = score_data.values.tolist()
    
    return render_template(
        "index.html", 
        score_data=score_data
    )

# "Add Score" Route
# Create an instance of the form "GetScoreData"
# When form is submitted from "add_score.html" template, save data to 
# corresponding variables.
# Write the data to the csv file
# Return to the index route to display data
@app.route('/add_score', methods=["GET","POST"])
def add_score():
    get_score_data = GetScoreData()
    if get_score_data.validate_on_submit():
        name = get_score_data.name.data
        score = get_score_data.score.data
        age_category = get_score_data.age_category.data
        email = get_score_data.email.data
        phone_num = get_score_data.phone_num.data
        
        with open(PATH, "a") as score_file:
            line = f"{name},{score},{age_category},{email},{phone_num}\n"
            score_file.write(line)
            
        return redirect(url_for(
            "index", _external=True, scheme="https"
        ))
        
    return render_template(
        "add_score.html", get_score_data=get_score_data
    )
        
    