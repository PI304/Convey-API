# Generated by Django 4.1.7 on 2023-02-20 23:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="QuestionAnswer",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("respondent_id", models.CharField(max_length=30)),
                ("answer", models.CharField(max_length=1000)),
            ],
            options={
                "db_table": "question_answer",
            },
        ),
        migrations.CreateModel(
            name="Respondent",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("respondent_id", models.CharField(max_length=30)),
            ],
            options={
                "db_table": "respondent",
            },
        ),
        migrations.CreateModel(
            name="SectorChoice",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("key", models.CharField(max_length=50)),
                ("value", models.CharField(max_length=200)),
            ],
            options={
                "db_table": "sector_choice",
            },
        ),
        migrations.CreateModel(
            name="SectorQuestion",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("content", models.CharField(max_length=200)),
                ("is_required", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "sector_question",
            },
        ),
        migrations.CreateModel(
            name="Survey",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=50)),
                ("description", models.CharField(max_length=200)),
                ("abbr", models.CharField(max_length=5)),
            ],
            options={
                "db_table": "survey",
            },
        ),
        migrations.CreateModel(
            name="SurveySector",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=50)),
                ("description", models.CharField(max_length=200)),
                (
                    "question_type",
                    models.SmallIntegerField(
                        choices=[
                            (0, "리커트"),
                            (1, "단답형"),
                            (2, "단일 선택"),
                            (3, "다중 선택"),
                            (4, "정도"),
                            (5, "서술형"),
                        ]
                    ),
                ),
                (
                    "survey",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="surveys.survey"
                    ),
                ),
            ],
            options={
                "db_table": "survey_sector",
            },
        ),
    ]
