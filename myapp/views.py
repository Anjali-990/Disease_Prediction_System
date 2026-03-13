# Django shortcuts and HTTP
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

# Authentication
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView

# Admin & CSRF
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

# Models and forms
from .models import PredictionHistory, Alert
from .forms import SignupForm, LoginForm

# Utilities
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta
import csv
import json
from reportlab.pdfgen import canvas
import joblib
import os
import numpy as np
#chnge pass
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
# Custom modules
from .urgency_map import DISEASE_URGENCY

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model = joblib.load(os.path.join(BASE_DIR, "myapp", "best_model.pkl"))
label_encoder = joblib.load(os.path.join(BASE_DIR, "myapp", "label_encoder.pkl"))
# ------------------------------
# HOME PAGE
# ------------------------------
def index(request):
    # Last 7 days disease trends
    last_7_days = timezone.now() - timedelta(days=7)

    disease_trends = (
        PredictionHistory.objects
        .filter(created_at__gte=last_7_days)
        .values("result")
        .annotate(count=Count("result"))
        .order_by("-count")[:5]
    )

    recent_predictions = None
    user_chart_data = None

    if request.user.is_authenticated:
        recent_predictions = (
            PredictionHistory.objects
            .filter(user=request.user)
            .order_by("-created_at")[:5]
        )

        user_chart_data = (
            PredictionHistory.objects
            .filter(user=request.user)
            .values("result")
            .annotate(count=Count("result"))
        )

    context = {
        "disease_trends": disease_trends,
        "recent_predictions": recent_predictions,
        "user_chart_data": user_chart_data,
    }

    return render(request, "index.html", context)


# ------------------------------
#Profile Page
# ------------------------------
@login_required
def profile(request):

    prediction_count = PredictionHistory.objects.filter(user=request.user).count()

    if "password_changed" in request.GET:
        messages.success(request, "✅ Your password has been updated successfully!")

    context = {
        "prediction_count": prediction_count
    }

    return render(request,"profile.html",context)

#---------------------------
#about
#--------------------------
def about(request):
    return render(request, "about.html")
#--------------------------
#change password views
#--------------------------

class CustomPasswordChangeView(PasswordChangeView):
    template_name = "change_password.html"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, "Password updated successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Failed to update password. Please check the fields and try again.")
        return super().form_invalid(form)
    
# ------------------------------
# USER DASHBOARD
# ------------------------------
@login_required
def user_dashboard(request):
    # Recent predictions by this user
    recent_predictions = PredictionHistory.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    # Outbreak alerts - top diseases in last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    
    disease_trends = PredictionHistory.objects.filter(
        created_at__gte=seven_days_ago
    ).values('result').annotate(count=Count('id')).order_by('-count')[:5]

    # Alerts from Alert model
    recent_alerts = Alert.objects.filter(
        triggered_at__gte=seven_days_ago
    ).order_by('-triggered_at')[:5]

    # Prepare data for charts (JS)
    labels = [trend['result'] for trend in disease_trends]
    counts = [trend['count'] for trend in disease_trends]

    daily_labels = []
    daily_counts = []
    for i in range(7, 0, -1):
        day = timezone.now() - timedelta(days=i)
        day_str = day.strftime('%Y-%m-%d')
        daily_labels.append(day_str)
        count = PredictionHistory.objects.filter(
            created_at__date=day.date()
        ).count()
        daily_counts.append(count)

    return render(request, "user_dashboard.html", {
        "recent_predictions": recent_predictions,
        "alerts": recent_alerts,
        "disease_trends": disease_trends,
        "labels_json": json.dumps(labels),
        "counts_json": json.dumps(counts),
        "daily_labels_json": json.dumps(daily_labels),
        "disease_line_data_json": json.dumps(daily_counts),
    })

#------------------------
# SIGNUP & LOGIN
#------------------------
def signup_view(request):

    if request.method == "POST":
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            messages.success(request,"Account created successfully")
            return redirect('login')

    else:
        form = SignupForm()

    return render(request,'signup.html',{'form':form})

#LOGIN
def login_view(request):

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username,password=password)

            if user:
                login(request,user)
                messages.success(request,"Login successful")
                return redirect('index')
            else:
                messages.error(request,"Invalid username or password")

    else:
        form = LoginForm()

    return render(request,'login.html',{'form':form})

# logout page
def logout_view(request):
    logout(request)
    return redirect('index')

#FORGOT PASSWORD
def forgot_password(request):
    return render(request, "forgot.html")

# ------------------------------
# PREDICTION PAGE
# ------------------------------
@login_required
def prediction(request):
    return render(request, "prediction.html")


# ------------------------------
# API: Predict Disease
# ------------------------------

@csrf_exempt
def predict_disease(request):

    if request.method == "POST":
        print("Received symptoms:", request.POST)
        fever = 1 if "fever" in request.POST else 0
        headache = 1 if "headache" in request.POST else 0
        nausea = 1 if "nausea" in request.POST else 0
        vomiting = 1 if "vomiting" in request.POST else 0
        fatigue = 1 if "fatigue" in request.POST else 0
        joint_pain = 1 if "joint_pain" in request.POST else 0
        skin_rash = 1 if "skin_rash" in request.POST else 0
        cough = 1 if "cough" in request.POST else 0
        weight_loss = 1 if "weight_loss" in request.POST else 0
        yellow_eyes = 1 if "yellow_eyes" in request.POST else 0
        

        input_data = np.array([[

            fever,
            headache,
            nausea,
            vomiting,
            fatigue,
            joint_pain,
            skin_rash,
            cough,
            weight_loss,
            yellow_eyes

        ]])
        
        # Predict disease
        prediction = model.predict(input_data)[0]

        # Decode disease name
        disease_name = label_encoder.inverse_transform([prediction])[0]

        # Get probability
        probabilities = model.predict_proba(input_data)

        #urgency and test
        info = DISEASE_URGENCY.get(disease_name, {})
        urgency = info.get("urgency", "Consult a doctor")
        tests = info.get("tests", "General health checkup")
        advisory = info.get("advisory", "Please consult a healthcare professional.")

        confidence = float(np.max(probabilities)) * 100
        print("Input data:", input_data)
        print("Model prediction:", prediction)
        print("Disease name:", disease_name)

        # Store symptoms as text
        selected_symptoms = []

        if fever:
            selected_symptoms.append("Fever")

        if headache:
            selected_symptoms.append("Headache")

        if nausea:
            selected_symptoms.append("Nausea")

        if vomiting:
            selected_symptoms.append("Vomiting")

        if fatigue:
            selected_symptoms.append("Fatigue")

        if joint_pain:
            selected_symptoms.append("Joint Pain")

        if skin_rash:
            selected_symptoms.append("Skin Rash")

        if cough:
            selected_symptoms.append("Cough")

        if weight_loss:
            selected_symptoms.append("Weight Loss")

        if yellow_eyes:
            selected_symptoms.append("Yellow Eyes")


        symptoms_text = ", ".join(selected_symptoms)

        # Save to database
        if request.user.is_authenticated:
            PredictionHistory.objects.create(
                user=request.user,
                symptoms=symptoms_text,
                result=disease_name,
                confidence=round(confidence,2),
                urgency=urgency,
                tests=tests
            )
        return JsonResponse({
            "prediction": disease_name,
            "confidence": round(confidence,2),
            "urgency": urgency,
            "tests": tests,
            "advisory": advisory
        })

    return JsonResponse({"error":"Invalid request"})

# ------------------------------
# HISTORY PAGE
# ------------------------------
@login_required
def history(request):

    user_history = PredictionHistory.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request,"history.html",{
        "history": user_history
    })
# ------------------------------
# EXPORT CSV
# ------------------------------
@login_required
def export_history_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="prediction_history.csv"'

    writer = csv.writer(response)

    # Header
    writer.writerow(["Date", "Symptoms", "Result", "Confidence"])

    for p in PredictionHistory.objects.filter(user=request.user):
        writer.writerow([
            p.created_at,
            p.symptoms,
            p.result,
            p.confidence
        ])

    return response


# ------------------------------
# EXPORT PDF
# ------------------------------
from django.http import HttpResponse
from reportlab.pdfgen import canvas

@login_required
def export_history_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="prediction_history.pdf"'

    p = canvas.Canvas(response)

    history = PredictionHistory.objects.filter(user=request.user)

    y = 800
    p.setFont("Helvetica", 10)

    p.drawString(200, 820, "Disease Prediction History")

    for item in history:
        text = f"{item.created_at} | {item.result} | {item.confidence}%"
        p.drawString(50, y, text)
        y -= 20

        if y < 100:
            p.showPage()
            y = 800

    p.save()
    return response

#---------------------------
#admin dashboard
#---------------------------
@staff_member_required
def admin_dashboard(request):

    # -----------------------------
    # 1️⃣ ALERTS (Last 24 hours)
    # -----------------------------
    last_24h = timezone.now() - timedelta(hours=24)

    alerts_query = (
        PredictionHistory.objects
        .filter(created_at__gte=last_24h)
    .values("result")
    .annotate(case_count=Count("id"))
    .order_by("-case_count")[:5]
)

    alert_list = []

    for a in alerts_query:

        count = a["case_count"]

        if count >= 5:
            risk = "high"
            icon = "🔴"
        elif count >= 3:
            risk = "medium"
            icon = "🟡"
        else:
            risk = "low"
            icon = "🟢"

        alert_list.append({
            "disease": a["result"],
            "count": count,
            "risk": risk,
            "icon": icon
        })


    # -----------------------------
    # 2️⃣ Disease Trends (7 days)
    # -----------------------------
    last_week = timezone.now() - timedelta(days=7)

    trends = (
    PredictionHistory.objects
    .filter(created_at__gte=last_week)
    .values("result")
    .annotate(count=Count("id"))
    .order_by("-count")[:10]
)

    disease_trends = trends


    # Chart Data
    labels = [t["result"] for t in trends]
    counts = [t["count"] for t in trends]


    # -----------------------------
    # 3️⃣ Daily Progression
    # -----------------------------
    daily_labels = []
    disease_line_data = {}

    for i in range(7):

        day = timezone.now().date() - timedelta(days=6-i)
        daily_labels.append(day.strftime("%Y-%m-%d"))

        day_records = (
            PredictionHistory.objects
            .filter(created_at__date=day)
            .values("result")
            .annotate(count=Count("id"))
        )

        for record in day_records:

            disease = record["result"]

            if disease not in disease_line_data:
                disease_line_data[disease] = [0]*7

            disease_line_data[disease][i] = record["count"]


    # -----------------------------
    # Context
    # -----------------------------
    context = {
        "alerts": alert_list,
        "disease_trends": disease_trends,
        "labels_json": json.dumps(labels),
        "counts_json": json.dumps(counts),
        "daily_labels_json": json.dumps(daily_labels),
        "disease_line_data_json": json.dumps(disease_line_data),
    }

    return render(request, "admin_dashboard.html", context)