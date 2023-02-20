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
    class QuestionType(models.IntegerChoices):
        LIKERT = 0, "리커트"
        SHORT_ANSWER = 1, "단답형"
        SINGLE_SELECT = 2, "단일 선택"
        MULTI_SELECT = 3, "다중 선택"
        EXTENT = 4, "정도"
        LONG_ANSWER = 5, "서술형"

    id = models.BigAutoField(primary_key=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=False)
    description = models.CharField(max_length=200, null=False)
    question_type = models.SmallIntegerField(
        null=False,
        choices=QuestionType.choices,
    )

    class Meta:
        db_table = "survey_sector"

    def __str__(self):
        return f"[{self.id}] {self.title}"

    def __repr__(self):
        return f"SurveySector({self.id}, {self.title})"


class SectorChoice(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    sector = models.ForeignKey(SurveySector, on_delete=models.CASCADE)
    key = models.CharField(max_length=50, null=False)
    value = models.CharField(max_length=200, null=False)

    class Meta:
        db_table = "sector_choice"

    def __str__(self):
        return f"[{self.id}] key: {self.key}/value: {self.value}"

    def __repr__(self):
        return f"SurveySector({self.id}, {self.key}, {self.value})"


class SectorQuestion(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    sector = models.ForeignKey(SurveySector, on_delete=models.CASCADE)
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
