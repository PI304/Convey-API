# Generated by Django 4.1.7 on 2023-02-27 12:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("survey_packages", "0003_alter_surveypackage_logo_and_more"),
        ("workspaces", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="routine",
            name="kick_off",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="kick_off_for",
                to="survey_packages.surveypackage",
            ),
        ),
        migrations.AddField(
            model_name="workspace",
            name="access_code",
            field=models.CharField(default=111111, max_length=128),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="routine",
            name="workspace",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="routine",
                to="workspaces.workspace",
            ),
        ),
        migrations.AlterField(
            model_name="routinedetail",
            name="routine",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="routine_details",
                to="workspaces.routine",
            ),
        ),
    ]
