import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

  dependencies = [
    ("collector", "0012_activityidsequence"),
  ]

  operations = [
    migrations.CreateModel(
      name="LargeGroupRecord",
      fields=[
        ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
        ("created_at", models.DateTimeField(auto_now_add=True)),
        ("building_id", models.CharField(db_index=True, max_length=128)),
        ("floor_id", models.CharField(db_index=True, max_length=128)),
        ("actor_id", models.CharField(blank=True, max_length=128)),
        ("size_band", models.CharField(max_length=64)),
        ("gender_composition", models.CharField(max_length=32)),
        ("age_composition", models.CharField(max_length=64)),
        ("activity_description", models.TextField()),
        ("activity_time", models.DateTimeField(db_index=True)),
        ("notes", models.TextField(blank=True)),
        ("location_x_pct", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
        ("location_y_pct", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
        ("photo_name", models.CharField(blank=True, max_length=255)),
        ("photo_object_name", models.CharField(blank=True, default="", max_length=512)),
        ("photo_preview_data_url", models.TextField(blank=True)),
        ("photo_latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        ("photo_longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
        ("photo_altitude", models.DecimalField(blank=True, decimal_places=2, max_digits=9, null=True)),
      ],
      options={
        "ordering": ["-activity_time", "-created_at"],
      },
    ),
  ]
