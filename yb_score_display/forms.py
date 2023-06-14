from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, SelectField, EmailField, IntegerField, TelField
from wtforms.validators import DataRequired
# validators.required(), validators.length(max=10)]

class GetScoreData(FlaskForm):
# Name, Score, Age Category, Email, Phone Number
    name = StringField("Name: ", validators=[DataRequired()])
    score = IntegerField("Score: ", validators=[DataRequired()])
    age_category = SelectField("Age Category: ", choices=["Senior", "Junior"])
    sex = SelectField("Sex: ", choices=["Gents", "Ladies", "Prefer not to say", "Other"])
    email = EmailField("Email: ")
    phone_num = StringField("Phone Number: ")
    
    submit = SubmitField("Submit")