from django.db import models
from django import forms
from django.contrib.auth.models import User

# Medical prediction history table
class PredictionHistory(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    symptoms = models.TextField()
    result = models.CharField(max_length=100)
    confidence = models.FloatField(blank=True, null=True)
    urgency = models.CharField(max_length=200)
    tests = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.result} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    
class Alert(models.Model):
    disease = models.CharField(max_length=100)
    message = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)
    cluster_size = models.IntegerField()

    predictions = models.ManyToManyField(PredictionHistory, related_name="alerts", blank=True)

    def __str__(self):
        return f"{self.disease} Alert ({self.cluster_size} cases)"

# Login form for modal
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password'}))
