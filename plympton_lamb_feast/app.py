from flask import Flask, render_template, request, redirect, url_for
from forms import GetScoreData

import pandas as pd

PATH = "static/scores.csv"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

@app.route('/', methods=["GET","POST"])
def index():
    score_data = pd.read_csv(PATH)
    score_data = score_data.sort_values(by=["score"], ascending=False)
    score_data = score_data.values.tolist()
    
    return render_template(
        "index.html", 
        score_data=score_data
    )

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
        
    