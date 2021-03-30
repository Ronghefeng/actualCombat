from django.db import models
from django.forms.models import model_to_dict


class Student(models.Model):

    GENDER = (
        (0, '男'),
        (1, '女')
    )

    name = models.CharField(max_length=32)
    age = models.IntegerField()
    gender = models.IntegerField(choices=GENDER, default=0)
    class_name = models.ForeignKey('ClassName',
                                   on_delete=models.SET_NULL,
                                   null=True)

    def serialize_for_audit_trail(self):
        return model_to_dict(self)


class ClassName(models.Model):

    name = models.CharField(max_length=32)
    count = models.IntegerField()

