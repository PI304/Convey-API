from typing import Union, List

from django.shortcuts import get_object_or_404

from apps.survey_packages.models import SurveyPackage
from apps.survey_packages.serializers import PackageContactSerializer


class SurveyPackageService(object):
    def __init__(self, package: Union[SurveyPackage, int]):
        if type(package) == int:
            self.package = get_object_or_404(SurveyPackage, id=package)
        else:
            self.package = package

    def add_contacts(self, contacts: List[dict]) -> SurveyPackage:
        for c in contacts:
            serializer = PackageContactSerializer(data=c)
            if serializer.is_valid(raise_exception=True):
                serializer.save(survey_package_id=self.package.id)

        return self.package
