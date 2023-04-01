# Generated by Django 4.1.7 on 2023-04-01 11:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("survey_packages", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="packagesubjectsurvey",
            name="number",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="packagesubjectsurvey",
            name="title",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
