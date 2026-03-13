import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import DBSCAN
from myapp.models import PredictionHistory, Alert
from django.utils import timezone
from datetime import timedelta
from collections import defaultdict
def run_clustering():
    last_24_hours = timezone.now() - timedelta(hours=24)
    records = PredictionHistory.objects.filter(date__gte=last_24_hours)  # changed here

    if not records.exists():
        return

    symptoms = [r.symptoms for r in records]
    diseases = [r.result for r in records]  # changed 'predicted_disease' to 'result'

    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(symptoms)

    model = DBSCAN(eps=1.5, min_samples=3)
    clusters = model.fit_predict(X.toarray())

    cluster_counts = {}
    for i, label in enumerate(clusters):
        if label == -1:
            continue
        disease = diseases[i]
        cluster_counts[(label, disease)] = cluster_counts.get((label, disease), 0) + 1

    # Merge clusters by disease to get total cases per disease
    disease_counts = defaultdict(int)
    for (_, disease), count in cluster_counts.items():
        disease_counts[disease] += count

    # Create alerts for diseases exceeding threshold
    for disease, total_count in disease_counts.items():
        if total_count < 5:
            continue  # skip small clusters

        # Check if an alert already exists in the last 24 hours
        exists = Alert.objects.filter(
            disease=disease,
            triggered_at__gte=last_24_hours
        ).exists()

        if not exists:
            Alert.objects.create(
                disease=disease,
                message=f"Potential outbreak: {disease} - {total_count} cases detected",
                cluster_size=total_count
            )