from django.utils import timezone
from datetime import timedelta
from collections import Counter
from .models import PredictionHistory, Alert

def generate_alerts():
    # get last 24h predictions
    last_24_hours = timezone.now() - timedelta(hours=24)
    recent_predictions = PredictionHistory.objects.filter(date__gte=last_24_hours)

    if not recent_predictions.exists():
        return

    # Count disease frequency
    disease_counts = Counter([p.result for p in recent_predictions])

    for disease, count in disease_counts.items():
        if count >= 5:  # threshold (you can adjust)
            # check if alert already exists for this disease today
            existing = Alert.objects.filter(
                disease=disease,
                triggered_at__gte=last_24_hours
            ).first()

            if not existing:
                alert = Alert.objects.create(
                    disease=disease,
                    message=f"Potential outbreak: {disease} - Cluster of {count} similar cases",
                    cluster_size=count
                )
                # link predictions to this alert
                alert.predictions.set([p for p in recent_predictions if p.result == disease])
