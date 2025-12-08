The Advanced Health Metric Predictor is a proof-of-concept application built on Django and TensorFlow/Keras. Its core function is to generate a highly contextual forecast of a patient's future health metrics (Blood Sugar, Blood Pressure, Cholesterol) based on a single snapshot of static and current data.

This project demonstrates a real-world machine learning deployment pipeline, moving beyond simple classification to complex multi-output regression using advanced feature engineering techniques.

Key Innovation: Feature Engineering for Trend Prediction

Instead of relying on the patient's difficult-to-obtain past lab results, the system uses a Feature Engineering layer to derive the crucial missing information from the inputs:
Key Innovation: Feature Engineering for Trend Prediction

Instead of relying on the patient's difficult-to-obtain past lab results, the system uses a Feature Engineering layer to derive the crucial missing information from the inputs. This process involves three critical features:

Velocity (Rate of Change): This feature uses the statistical trend learned from historical patient cohorts (e.g., how fast a 50-year-old typically reduces cholesterol) to determine if the metric is trending up or down.

Inertia (Responsiveness): This historical factor indicates how volatile or resistant to change a metric is for the patient's demographic. It dampens or amplifies the prediction, making it clinically plausible.

Contextual Risk Score: This is a weighted measure of Age and BMI influence that establishes a cautious risk floor, preventing over-optimistic predictions for high-risk patients.
🛠️ Setup and Installation

Prerequisites

You must have Python 3.10+ and MySQL (or switch to SQLite).

# Recommended Python dependencies
pip install django
pip install tensorflow
pip install numpy
pip install scikit-learn
# If using MySQL:
pip install mysqlclient



Deployment Workflow (Three Steps)

1. Database Configuration

Ensure your settings.py points to a functioning database (MySQL or SQLite).

2. Initialize and Migrate

Apply the database structure and create the necessary tables, including Django's built-in User tables.

python manage.py makemigrations predictor
python manage.py migrate
python manage.py createsuperuser 
3. Run the Server

The application will start, and the FNN will train its simulated weights into memory upon the first import of predictor/fnn_predictor.py.

python manage.py runserver



Accessing the Application

Homepage (Login): http://127.0.0.1:8000/

Input Form: Accessible after logging in with the superuser credentials.
