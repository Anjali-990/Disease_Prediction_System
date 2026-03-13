from django.core.management.base import BaseCommand
from myapp.cluster_analysis import run_clustering

class Command(BaseCommand):
    help = "Run symptom clustering and generate alerts"

    def handle(self, *args, **kwargs):
        run_clustering()
        self.stdout.write(self.style.SUCCESS("Clustering completed successfully"))
