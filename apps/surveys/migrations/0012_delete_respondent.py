# Generated by Django 4.1.7 on 2023-03-08 06:56

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0011_questionanswer_user"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Respondent",
        ),
    ]
