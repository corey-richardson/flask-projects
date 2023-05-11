class GetPassengerForm(FlaskForm):
    sex = RadioField(
        "Sex", 
        choices=[(0.0, "Male"), (1.0, "Female")])
    age = StringField("Age: ", validators=[DataRequired()])
    p_class = RadioField(
        "Class", 
        choices=[("1", "First"), ("2","Second"), ("3","Third")])
    submit = SubmitField("Submit")