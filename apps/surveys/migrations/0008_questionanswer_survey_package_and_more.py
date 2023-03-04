# Generated by Django 4.1.7 on 2023-03-04 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("survey_packages", "0009_remove_surveypackage_workspace"),
        ("surveys", "0007_sectorquestion_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="questionanswer",
            name="survey_package",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="survey_packages.surveypackage",
            ),
        ),
        migrations.AlterField(
            model_name="questionanswer",
            name="question",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="surveys.sectorquestion"
            ),
        ),
    ]