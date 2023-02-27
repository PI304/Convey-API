from rest_framework import serializers

from apps.surveys.models import Survey


class SurveySerialzer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"
