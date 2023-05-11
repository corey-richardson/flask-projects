from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from forms import GetPassengerForm

import pandas as pd
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

# Generate Model
## Load CSV Passenger data
passengers = pd.read_csv("static/passengers.csv")

## Cleanse Data
passengers["Sex"] = passengers["Sex"].map({"female":1, "male":0})
passengers["Age"].fillna(value=passengers["Age"].mean(), inplace=True)
passengers["FirstClass"] = passengers['Pclass'].apply(
    lambda x: 1 if x == 1 else 0 )
passengers["SecondClass"] = passengers['Pclass'].apply(
    lambda x: 1 if x == 2 else 0 )

## Select feature data
features = passengers[["Sex", "Age", "FirstClass", "SecondClass"]]
survival = passengers["Survived"]

## Split the data into model and testing data
X_train, X_test, y_train, y_test = train_test_split(
  features, survival, test_size = 0.2, random_state = 1)

## Normalise the data
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

## Fit the model
model = LogisticRegression()
model.fit(X_train, y_train)

## Test the model
print(f"Train Model Score: {model.score(X_train_scaled, y_train)}")
print(f"Test Model Score: {model.score(X_test, y_test)}")

# 
@app.route('/', methods=["GET","POST"])
def index():
    get_passenger_form = GetPassengerForm()

    ## Validate form
    if get_passenger_form.validate_on_submit():
        sex = get_passenger_form.sex.data
        age = get_passenger_form.age.data
        p_class = get_passenger_form.p_class.data

        ## Data formatting
        first, second = 0, 0
        if p_class == "1":
            first = 1
        elif p_class == "2":
            second = 1

        ## Cast all to floats
        sex, age, first, second = float(sex), float(age), float(first), float(second)

        ## Use the model to predict
        survived = model.predict( [[sex, age, first, second ]] )
        p_survived = model.predict_proba( [[sex, age, first, second ]] )
        print(survived)

        return render_template( # should use redirect here but wouldnt work oops
            "submit.html",
            sex = sex,
            age = age,
            first = first,
            second = second,
            survived = survived[0],
            p_survived = p_survived[0][1]*100, # deci --> pct
            _external=True, _scheme='https')

    return render_template("index.html", get_passenger_form=get_passenger_form)

