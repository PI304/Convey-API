# Generated by Django 4.1.7 on 2023-03-09 21:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import shortuuid.django_fields


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PackageContact",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "type",
                    models.CharField(
                        choices=[("email", "이메일"), ("phone", "휴대폰 번호")], max_length=10
                    ),
                ),
                ("content", models.CharField(max_length=50)),
            ],
            options={
                "db_table": "package_contact",
            },
        ),
        migrations.CreateModel(
            name="PackagePart",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=100)),
            ],
            options={
                "db_table": "package_part",
            },
        ),
        migrations.CreateModel(
            name="PackageSubject",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("number", models.PositiveIntegerField()),
                ("title", models.CharField(max_length=100)),
            ],
            options={
                "db_table": "package_subject",
            },
        ),
        migrations.CreateModel(
            name="PackageSubjectSurvey",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=100, null=True)),
                ("number", models.PositiveIntegerField(null=True)),
            ],
            options={
                "db_table": "package_subject_survey",
            },
        ),
        migrations.CreateModel(
            name="SurveyPackage",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=100)),
                ("logo", models.ImageField(null=True, upload_to="package_logo/")),
                ("access_code", models.CharField(max_length=10)),
                (
                    "uuid",
                    shortuuid.django_fields.ShortUUIDField(
                        alphabet=None, length=22, max_length=22, prefix=""
                    ),
                ),
                ("is_closed", models.BooleanField(default=False)),
                ("description", models.CharField(max_length=200)),
                ("manager", models.CharField(max_length=10)),
                (
                    "author",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "survey_package",
            },
        ),
        migrations.CreateModel(
            name="Respondent",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("respondent_id", models.CharField(max_length=30)),
                (
                    "survey_package",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to="survey_packages.surveypackage",
                    ),
                ),
            ],
            options={
                "db_table": "respondent",
            },
        ),
    ]
