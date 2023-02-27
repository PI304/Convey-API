# Generated by Django 4.1.7 on 2023-02-22 11:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.PositiveSmallIntegerField(
                choices=[(0, "admin"), (1, "subject")], default=0
            ),
            preserve_default=False,
        ),
    ]
