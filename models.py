from django.db import models
from django.core.validators import MinValueValidator,MaxValueValidator

class PredictionRecord(models.Model):

    Username = models.CharField(max_length=20,blank=True)
    Password = models.CharField(max_length=15,blank=True)
    Metric_type = models.CharField(max_length=20,help_text="Type of test to be taken (e.g.,Cholesterol,BP,Sugar)")
    Current_metric_value = models.FloatField()
    Age = models.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(120)])
    Gender = models.FloatField()
    Weight_kg = models.FloatField()
    height_cm = models.FloatField()

    bmi = models.FloatField(help_text="Body Mass Index Calculated from weight and height")
    Health_score = models.FloatField(help_text="The final predicted health score from the FNN")

    Prediction_timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction for user {self.Username or "Anonymous"} at {self.Prediction_timestamp('%Y-%m-%d %H:%M')}"