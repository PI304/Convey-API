from django.db import models


class TimeStampMixin(models.Model):
    """
    abstract timestamp mixin base model for created_at, updated_at field
    """

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    """
    abstract soft delete mixin base model for is_deleted field
    """

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True
