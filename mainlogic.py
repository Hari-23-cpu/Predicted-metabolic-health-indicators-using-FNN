import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import math
import random

RISK_PARAMETERS = {
    'AGE_RISK_SCALE': 0.8,
    'BMI_RISK_SCALE': 1.5,
    'INTERACTION_SCALE': 0.00005,
    'BASELINE_NOISE_STD_G': 2.0, 
    'BASELINE_NOISE_STD_B': 3.0,
    'BASELINE_NOISE_STD_C': 4.0,
    'STOCHASTIC_FACTOR': 2.5 
}

THRESHOLDS = {
    'Cholesterol': {'high': 240, 'medium': 200},
    'BP': {'high': 140, 'medium': 130},
    'Glucose': {'high': 125, 'medium': 100}
}

def calculate_bmi(weight_kg, height_cm):
    return weight_kg / (height_cm / 100)**2 if height_cm > 0 else 0

def calculate_worsening_delta(current_metric, metric_type, age, bmi, current_bp, current_cholesterol, current_glucose):
    age_factor = max(0, age - 45) / 10.0
    bmi_factor = max(0, bmi - 28) / 5.0
    threshold_high = THRESHOLDS[metric_type]['high']
    value_escalation = max(0, current_metric - threshold_high) / 20.0
    cross_metric_influence = 0.0
    
    if metric_type == 'Glucose':
        bp_influence = max(0, current_bp - 130) / 30.0
        cholesterol_influence = max(0, current_cholesterol - 200) / 40.0
        cross_metric_influence = (bp_influence + cholesterol_influence) * 0.5

    elif metric_type == 'BP':
        glucose_influence = max(0, current_glucose - 100) / 20.0
        cholesterol_influence = max(0, current_cholesterol - 200) / 40.0
        cross_metric_influence = (glucose_influence + cholesterol_influence) * 0.4

    elif metric_type == 'Cholesterol':
        glucose_influence = max(0, current_glucose - 100) / 30.0
        cross_metric_influence = glucose_influence * 0.3 + bmi_factor * 0.2

    delta = 1.0 + (age_factor * 0.5) + (bmi_factor * 0.8) + (value_escalation * 1.5) + cross_metric_influence
    return max(0.5, delta) 

def generate_synthetic_dataset(n_samples=25000):
    genders = ['male', 'female']
    n_samples = 25000 
    ages = np.random.normal(55, 12, n_samples).astype(int) 
    heights = np.random.uniform(160, 195, n_samples)
    weights = np.random.normal(90, 20, n_samples) 
    cholesterol_levels = np.random.uniform(150, 300, n_samples)
    systolic_bps = np.random.normal(130, 15, n_samples)
    glucose_levels = np.random.normal(110, 25, n_samples)

    data = []
    
    for i in range(n_samples):
        age = np.clip(ages[i], 35, 90)
        w = np.clip(weights[i], 50, 180)
        h = heights[i]
        
        cholesterol = np.clip(cholesterol_levels[i], 150, 350)
        bp = np.clip(systolic_bps[i], 100, 190)
        glucose = np.clip(glucose_levels[i], 70, 300)

        gender = np.random.choice(genders)
        bmi = calculate_bmi(w, h)
        
        delta_glucose = calculate_worsening_delta(glucose, 'Glucose', age, bmi, bp, cholesterol, glucose)
        delta_bp = calculate_worsening_delta(bp, 'BP', age, bmi, bp, cholesterol, glucose)
        delta_cholesterol = calculate_worsening_delta(cholesterol, 'Cholesterol', age, bmi, bp, cholesterol, glucose)

        noise_g = np.random.normal(0, RISK_PARAMETERS['BASELINE_NOISE_STD_G'])
        noise_b = np.random.normal(0, RISK_PARAMETERS['BASELINE_NOISE_STD_B'])
        noise_c = np.random.normal(0, RISK_PARAMETERS['BASELINE_NOISE_STD_C'])
        
        future_glucose = glucose + delta_glucose + noise_g
        future_bp = bp + delta_bp + noise_b
        future_cholesterol = cholesterol + delta_cholesterol + noise_c

        future_glucose = np.clip(future_glucose, 70, 400)
        future_bp = np.clip(future_bp, 90, 210)
        future_cholesterol = np.clip(future_cholesterol, 150, 450)
        
        feature_vector = [
            age, 
            (0 if gender == 'female' else 1), 
            bmi, 
            glucose, 
            bp, 
            cholesterol, 
            delta_glucose, 
            delta_bp,      
            delta_cholesterol,
            delta_glucose * delta_bp * delta_cholesterol 
        ]
        
        target_vector = [future_glucose, future_bp, future_cholesterol]
        
        data.append(feature_vector + target_vector)
        
    data_array = np.array(data)
    return data_array[:, :-3], data_array[:, -3:] 

def define_and_load_model():
    """Defines and simulates training/loading the Multi-Output FNN model ONCE."""
    print("--- Simulating Multi-Output FNN Model Training for Deployment ---")
    try:
        X_train, Y_train = generate_synthetic_dataset() 
        model = Sequential([
            Dense(256, activation='elu', input_shape=(X_train.shape[1],)),
            Dense(128, activation='elu'),
            Dense(64, activation='elu'),
            Dense(32, activation='elu'),
            Dense(3, activation='linear') 
        ])
        
        model.compile(optimizer='nadam', loss='mean_squared_error') 
        
        model.fit(X_train, Y_train, epochs=80, batch_size=128, verbose=0)
        model.trainable = False
        print("--- Multi-Output FNN Model Trained and loaded into memory ---")
        return model
    except Exception as e:
        print(f"Error initializing FNN Model (TensorFlow/NumPy): {e}")
        return None

FNN_MODEL = define_and_load_model()

def predict_outcome_with_fnn(glucose_level, systolic_bp, cholesterol_level, age, gender, weight_kg, height_cm):

    
    bmi = calculate_bmi(weight_kg, height_cm)
    delta_glucose = calculate_worsening_delta(glucose_level, 'Glucose', age, bmi, systolic_bp, cholesterol_level, glucose_level)
    delta_bp = calculate_worsening_delta(systolic_bp, 'BP', age, bmi, systolic_bp, cholesterol_level, glucose_level)
    delta_cholesterol = calculate_worsening_delta(cholesterol_level, 'Cholesterol', age, bmi, systolic_bp, cholesterol_level, glucose_level)
    
    input_vector = np.array([[
        age, 
        (0 if gender.lower() == 'female' else 1),
        bmi, 
        glucose_level, 
        systolic_bp, 
        cholesterol_level, 
        delta_glucose, 
        delta_bp,      
        delta_cholesterol,
        delta_glucose * delta_bp * delta_cholesterol
    ]])
    
    future_g, future_bp, future_c = None, None, None
    
    if FNN_MODEL is None:
        print("Model not initialized. Returning baseline delta projections.")
        future_g = glucose_level + delta_glucose
        future_bp = systolic_bp + delta_bp
        future_c = cholesterol_level + delta_cholesterol
    else:
        try:
            prediction_vector = FNN_MODEL.predict(input_vector, verbose=0)[0]
            future_g, future_bp, future_c = prediction_vector
            future_g = round(max(70, future_g + random.uniform(-1, 1)), 1)
            future_bp = round(max(90, future_bp + random.uniform(-1, 1)), 1)
            future_c = round(max(150, future_c + random.uniform(-1, 1)), 1)
            
        except Exception as e:
            print(f"Prediction failed: {e}")
            future_g = glucose_level + delta_glucose
            future_bp = systolic_bp + delta_bp
            future_c = cholesterol_level + delta_cholesterol
    
    return {
        'future_glucose_level': future_g,
        'future_systolic_bp': future_bp,
        'future_cholesterol_level': future_c,
        'derived_risk_factors': {
            'BMI': round(bmi, 2),
            'Glucose Delta Factor': round(delta_glucose, 2),
            'BP Delta Factor': round(delta_bp, 2),
            'Cholesterol Delta Factor': round(delta_cholesterol, 2)
        }
    }