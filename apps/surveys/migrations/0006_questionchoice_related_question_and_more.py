# Generated by Django 4.1.7 on 2023-03-02 23:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("surveys", "0005_choicesset_questionchoice_delete_sectorchoice_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="questionchoice",
            name="related_question",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="choices",
                to="surveys.sectorquestion",
            ),
        ),
        migrations.AddField(
            model_name="questionchoice",
            name="related_sector",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="common_choices",
                to="surveys.surveysector",
            ),
        ),
        migrations.DeleteModel(
            name="ChoicesSet",
        ),
    ]