# Generated by Django 4.1.7 on 2023-03-09 16:44

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0012_delete_respondent"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sectorquestion",
            name="number",
            field=models.FloatField(),
        ),
    ]