from django.db import models
from shortuuid.django_fields import ShortUUIDField

from apps.surveys.models import Survey
from apps.users.models import User
from config.mixins import TimeStampMixin


class SurveyPackage(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100, null=False)
    logo = models.ImageField(blank=False, null=True, upload_to="package_logo/")
    access_code = models.CharField(max_length=10, null=False)
    uuid = ShortUUIDField()
    is_closed = models.BooleanField(default=False)
    description = models.CharField(max_length=200, null=False)
    manager = models.CharField(max_length=10, null=False)

    class Meta:
        db_table = "survey_package"

    def __str__(self):
        return f"[{self.id}] {self.title}"

    def __repr__(self):
        return f"SurveyPackage({self.id}, {self.title})"


class PackageComposition(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    survey_package = models.ForeignKey(SurveyPackage, on_delete=models.CASCADE)

    class Meta:
        db_table = "package_composition"

    def __str__(self):
        return f"[{self.id}] survey: {self.survey_id}/package: {self.survey_package_id}"

    def __repr__(self):
        return (
            f"PackageComposition({self.id}, {self.survey_id}-{self.survey_package_id})"
        )


class PackageContact(TimeStampMixin):
    class ContactType(models.TextChoices):
        EMAIL = "email", "이메일"
        PHONE_NUMBER = "phone", "휴대폰 번호"

    id = models.BigAutoField(primary_key=True)
    survey_package = models.ForeignKey(
        SurveyPackage, on_delete=models.CASCADE, related_name="contacts"
    )
    type = models.CharField(null=False, choices=ContactType.choices, max_length=10)
    content = models.CharField(max_length=50, null=False)

    class Meta:
        db_table = "package_contact"

    def __str__(self):
        return f"[{self.id}] {self.content}"

    def __repr__(self):
        return f"PackageContact({self.id}, {self.content})"


class PackagePart(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100, null=False)
    survey_package = models.ForeignKey(
        SurveyPackage, on_delete=models.CASCADE, null=False, related_name="parts"
    )

    class Meta:
        db_table = "package_part"

    def __str__(self):
        return f"[{self.id}] {self.title}"

    def __repr__(self):
        return f"PackagePart({self.id}, {self.title})"


class PackageSubject(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    number = models.PositiveIntegerField(null=False)
    title = models.CharField(max_length=100, null=False)
    package_part = models.ForeignKey(
        PackagePart, null=False, on_delete=models.CASCADE, related_name="subjects"
    )

    class Meta:
        db_table = "package_subject"

    def __str__(self):
        return f"[{self.id}] {self.title}"

    def __repr__(self):
        return f"PackageSubject({self.id}, {self.title})"


class PackageSubjectSurvey(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    subject = models.ForeignKey(
        PackageSubject, null=False, on_delete=models.CASCADE, related_name="surveys"
    )
    survey = models.ForeignKey(
        Survey, null=False, on_delete=models.CASCADE, related_name="survey_content"
    )
    title = models.CharField(max_length=100, null=True)
    number = models.PositiveIntegerField(null=True)

    class Meta:
        db_table = "package_subject_survey"

    def __str__(self):
        return f"[{self.id}] ({self.subject}, {self.survey})"

    def __repr__(self):
        return f"PackageSubjectSurvey({self.id}, ({self.subject}, {self.survey}))"
