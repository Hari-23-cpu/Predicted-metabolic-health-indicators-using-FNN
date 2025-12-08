from django.shortcuts import render, redirect
from django.http import HttpResponse # Keep this for generic responses if needed
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

# Ensure these imports are correct based on your project structure
from .forms import PredictionInputForm 
from .mainlogic import predict_outcome_with_fnn 

prediction_model = None 

# Define constants
MODEL_FEATURE_NAMES = [
    'age', 
    'bmi', 
    'glucose', 
    'bp', 
    'cholesterol', 
    'delta_glucose', 
    'delta_bp', 
    'delta_cholesterol',
    'delta_glucose * delta_bp * delta_cholesterol'
]

# --- Core View Functions ---

def login_view(request):
    """
    Handles user login.
    """
    if request.user.is_authenticated:
        return redirect('predictor:input_form')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST) 
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('predictor:input_form') 
        
    else: # GET request
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@login_required
def input_form_view(request):
    """
    Displays the form for health metric inputs.
    """
    form = PredictionInputForm()
    return render(request, 'input.html', {'form': form})

@login_required
def prediction_results_view(request):
    """
    Processes the input form, runs the FNN prediction logic, and displays results.
    """
    # Initialize variables 
    future_glucose = None
    future_bp = None
    future_cholesterol = None
    derived_factors = {}
    bmi = None
    data = {}

    # If the user accesses this page via a GET request (not a form submission), redirect them.
    if request.method != 'POST':
        return redirect('predictor:input_form')

    # Handle POST request
    form = PredictionInputForm(request.POST) 

    if form.is_valid():
        try:
            # 1. Extract All Cleaned Data
            data = form.cleaned_data
            age = data['age']
            gender = data['gender']
            weight_kg = data['weight_kg']
            height_cm = data['height_cm']

            # Extract the three core metrics
            glucose_level = data['glucose_level']
            systolic_bp = data['systolic_bp']
            cholesterol_level = data['cholesterol_level']

            # 2. Calculate BMI
            height_m = height_cm / 100.0
            bmi = round(weight_kg / (height_m**2), 2)
            
            # 3. Make Multi-Output Prediction
            prediction_data = predict_outcome_with_fnn(
                glucose_level, 
                systolic_bp, 
                cholesterol_level, 
                age, 
                gender, 
                weight_kg, 
                height_cm
            )
            
            # 4. Unpack the Results
            future_glucose = round(prediction_data['future_glucose_level'], 2)
            future_bp = round(prediction_data['future_systolic_bp'], 2)
            future_cholesterol = round(prediction_data['future_cholesterol_level'], 2)
            derived_factors = prediction_data['derived_risk_factors']
            
        except Exception as e:
            # Handle prediction errors gracefully
            print(f"Error during FNN prediction: {e}")
            future_glucose = "N/A (Error)"
            future_bp = "N/A (Error)"
            future_cholesterol = "N/A (Error)"
            derived_factors = {'Error': f"Prediction failed: {e}"}

    # Prepare Context for result.html
    context = {
        'form': form, # Pass the (potentially pre-filled) form back
        
        # Input Values
        'age': data.get('age'),
        'gender': data.get('gender'),
        'bmi': bmi,
        'glucose_level': data.get('glucose_level'),
        'systolic_bp': data.get('systolic_bp'),
        'cholesterol_level': data.get('cholesterol_level'),

        # Predicted Future Values (The new primary results)
        'future_glucose': future_glucose,
        'future_bp': future_bp,
        'future_cholesterol': future_cholesterol,
        
        # Derived factors 
        'derived_factors': derived_factors,
        
        # Summary text
        'prediction_summary': "The model projects the following future values based on the input data and calculated metric interactions.",
    }
    
    # Render the results page
    return render(request, 'result.html', context)