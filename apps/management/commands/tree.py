
from django.core.management.base import BaseCommand
from apps.models import AQILog
import pandas as pd
from sklearn.tree import DecisionTreeRegressor, export_text

class Command(BaseCommand):
    help = 'Train and display a decision tree for AQI based on features from DB'

    def handle(self, *args, **kwargs):
        # Ambil data dari database
        qs = AQILog.objects.all().values(
            'pm25', 'pm10', 'co', 'no2', 'so2', 'o3', 'aqi'
        )
        df = pd.DataFrame.from_records(qs)

        # Bersihkan data (drop yang ada NaN)
        df = df.dropna()

        # Pisahkan fitur dan target
        X = df[['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']]
        y = df['aqi']

        # Buat model pohon keputusan
        model = DecisionTreeRegressor(max_depth=3)  # Biar pohon tidak terlalu dalam
        model.fit(X, y)

        # Tampilkan pohon ke terminal
        tree_rules = export_text(model, feature_names=list(X.columns))
        self.stdout.write(self.style.SUCCESS("Decision Tree:\n"))
        self.stdout.write(tree_rules)
