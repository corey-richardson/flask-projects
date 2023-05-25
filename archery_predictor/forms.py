from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, IntegerField
from wtforms.validators import DataRequired

class GetScoreData(FlaskForm):
    distance = RadioField(
        "Distance",
        choices = [
            (10.0, "10 yards"),
            (19.685, "18 metres"),
            (20.0, "20 yards"),
            (30.0, "30 yards"),
            (40.0, "40 yards"),
            (50.0, "50 yards"),
            (54.6807, "50 metres"),
            (60, "60 yards"),
            (76.5529, "70 metres"),
            (80.0, "80 yards"),
            (100.0, "100 yards")
        ]
    )
    days_till = IntegerField("Days Till Shoot: ", validators=[DataRequired()])
    submit = SubmitField("Submit")