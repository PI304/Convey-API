# Generated by Django 4.1.7 on 2023-03-09 17:14

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("survey_packages", "0012_delete_packagecomposition"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Respondent",
        ),
    ]