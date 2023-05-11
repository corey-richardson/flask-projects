from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

import pandas as pd
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'

passengers = pd.read_csv("static/passengers.csv")

passengers["Sex"] = passengers["Sex"].map({"female":1, "male":0})
passengers["Age"].fillna(value=passengers["Age"].mean(), inplace=True)
passengers["FirstClass"] = passengers['Pclass'].apply(
    lambda x: 1 if x == 1 else 0 )
passengers["SecondClass"] = passengers['Pclass'].apply(
    lambda x: 1 if x == 2 else 0 )

features = passengers[["Sex", "Age", "FirstClass", "SecondClass"]]
survival = passengers["Survived"]

X_train, X_test, y_train, y_test = train_test_split(
  features, survival, test_size = 0.2, random_state = 1)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = LogisticRegression()
model.fit(X_train_scaled, y_train)

# Score the model on the train data
print(f"Train Model Score: {model.score(X_train_scaled, y_train)}")
# Score the model on the test data
print(f"Test Model Score: {model.score(X_test, y_test)}")

class GetPassengerForm(FlaskForm):
    sex = StringField("Sex: ", validators=[DataRequired()])
    age = StringField("Age: ", validators=[DataRequired()])
    p_class = RadioField(
        "Class", 
        choices=[(1, "First"), (2,"Second"), (3,"Third")])

    submit = SubmitField("SubmitName")

@app.route('/', methods=["GET","POST"])
def index():
    get_passenger_form = GetPassengerForm()
    sex = get_passenger_form.sex.data
    age = get_passenger_form.age.data
    p_class = get_passenger_form.p_class.data
    return render_template("index.html", get_passenger_form=get_passenger_form)

