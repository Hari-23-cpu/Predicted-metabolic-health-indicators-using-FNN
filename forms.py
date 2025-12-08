from django import forms

class PredictionInputForm(forms.Form):
    
    GENDER_CHOICES = [
        ('male','Male'),
        ('female','Female'),
    ]
    username = forms.CharField(
        label = "Username",
        max_length = 254,
        widget = forms.TextInput(
            attrs={'placeholder':'Enter username'}
        ),
    )
    password = forms.CharField(
        label = "Password",
        strip = False,
        widget = forms.PasswordInput(
            attrs={'placeholder':'Enter your Password'}
        ),
    )

    glucose_level = forms.FloatField(
        label="Blood Glucose (mg/dL)",
        min_value=1.0,
        required=False, # Make optional, validation will happen in the view
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 105'})
    )
    
    systolic_bp = forms.FloatField(
        label="Systolic BP (mmHg)",
        min_value=1.0,
        required=False, # Make optional
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 120'})
    )

    cholesterol_level = forms.FloatField(
        label="Total Cholesterol (mg/dL)",
        min_value=1.0,
        required=False, # Make optional
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 200'})
    )

    def clean(self):
        """Custom validation to ensure at least one metric is provided."""
        cleaned_data = super().clean()
        glucose = cleaned_data.get('glucose_level')
        bp = cleaned_data.get('systolic_bp')
        cholesterol = cleaned_data.get('cholesterol_level')

        if not (glucose or bp or cholesterol):
            self.add_error(None, "You must provide a value for at least one metric (Glucose, BP, or Cholesterol) to run the prediction.")

        return cleaned_data
    
    age = forms.IntegerField(
        label ="Age(Years)",
        min_value=18,
        max_value=100,
        widget =forms.NumberInput(attrs={'placeholder':'e.g.,45'})
    )
    gender = forms.ChoiceField(
        label="Gender",
        choices = GENDER_CHOICES
    )
    weight_kg = forms.FloatField(
        label="Weight(kg)",
        min_value=1.0,
        widget=forms.NumberInput(attrs={'placeholder':'e.g,85'})
    )

    height_cm =forms.FloatField(
        label="Height(cm)",
        min_value = 1.0,
        widget = forms.NumberInput(attrs={'placeholder':'e.g.,175'})
    )