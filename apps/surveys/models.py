from django.db import models

from apps.users.models import User
from config.mixins import TimeStampMixin


class Survey(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=200, null=False)
    abbr = models.CharField(max_length=5, null=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "survey"

    def __str__(self):
        return f"[{self.id}] {self.title}"

    def __repr__(self):
        return f"Survey({self.id}, {self.title})"


class SurveySector(TimeStampMixin):
    class QuestionType(models.TextChoices):
        LIKERT = "likert", "리커트"
        SHORT_ANSWER = "short_answer", "단답형"
        SINGLE_SELECT = "single_select", "단일 선택"
        MULTI_SELECT = "multi_select", "다중 선택"
        EXTENT = "extent", "정도"
        LONG_ANSWER = "long_answer", "서술형"

    id = models.BigAutoField(primary_key=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name="sectors")
    title = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=200, null=False)
    question_type = models.CharField(
        null=False, choices=QuestionType.choices, max_length=15
    )

    class Meta:
        db_table = "survey_sector"

    def __str__(self):
        return f"[{self.id}] {self.title}"

    def __repr__(self):
        return f"SurveySector({self.id}, {self.title})"


class SectorQuestion(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    sector = models.ForeignKey(
        SurveySector, on_delete=models.CASCADE, related_name="questions"
    )
    content = models.CharField(max_length=200, null=False)
    is_required = models.BooleanField(default=True)
    linked_sector = models.ForeignKey(
        SurveySector, on_delete=models.SET_NULL, null=True, related_name="linked_sector"
    )

    class Meta:
        db_table = "sector_question"

    def __str__(self):
        return f"[{self.id}] {self.content}"

    def __repr__(self):
        return f"SectorQuestion({self.id}, {self.content})"


class QuestionChoice(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    number = models.PositiveIntegerField(null=False)
    content = models.CharField(max_length=200, null=True)
    is_descriptive = models.BooleanField(null=False)
    desc_form = models.CharField(max_length=50, null=True)
    related_sector = models.ForeignKey(
        SurveySector, null=True, on_delete=models.CASCADE, related_name="common_choices"
    )
    related_question = models.ForeignKey(
        SectorQuestion, on_delete=models.CASCADE, null=True, related_name="choices"
    )

    class Meta:
        db_table = "question_choice"

    def __str__(self):
        return f"[{self.id}] {self.number}"

    def __repr__(self):
        return f"QuestionChoice({self.id}, {self.number})"


# class ChoicesSet(TimeStampMixin):
#     id = models.BigAutoField(primary_key=True)
#     sector = models.ForeignKey(SurveySector, null=True, on_delete=models.CASCADE, related_name="common_choices")
#     question = models.ForeignKey(
#         SectorQuestion, null=True, related_name="choices_set", on_delete=models.CASCADE
#     )
#     choice = models.ForeignKey(
#         QuestionChoice, null=False, on_delete=models.CASCADE, related_name="questions"
#     )
#
#     class Meta:
#         db_table = "choices_set"
#
#     def __str__(self):
#         return f"[{self.id}] {self.question_id} {self.choice_id}"
#
#     def __repr__(self):
#         return f"ChoicesSet({self.id}, {self.question_id}, {self.choice_id})"


class QuestionAnswer(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    question = models.ForeignKey(SectorQuestion, on_delete=models.SET_NULL, null=True)
    respondent_id = models.CharField(max_length=30, null=False)
    subject = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    answer = models.CharField(max_length=1000, null=False)

    class Meta:
        db_table = "question_answer"

    def __str__(self):
        return f"[{self.id}] {self.respondent_id}"

    def __repr__(self):
        return f"QuestionAnswer({self.id}, {self.respondent_id})"


class Respondent(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    respondent_id = models.CharField(max_length=30)
    survey_package = models.ForeignKey(
        "survey_packages.SurveyPackage", on_delete=models.DO_NOTHING
    )

    class Meta:
        db_table = "respondent"

    def __str__(self):
        return f"[{self.id}] {self.respondent_id}/package: {self.survey_package_id}"

    def __repr__(self):
        return f"Respondent({self.id}, {self.respondent_id}, {self.survey_package_id})"
