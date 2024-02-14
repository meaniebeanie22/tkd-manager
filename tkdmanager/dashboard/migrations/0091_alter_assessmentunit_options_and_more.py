# Generated by Django 5.0.1 on 2024-02-14 10:09

from django.db import migrations
from django.shortcuts import get_object_or_404
# need to rename assessmentunittypes

ASSESSMENT_UNITS = [
    ('SD','Self Defense'),
    ('SE','Self Develop'),
    ('PA1','1st Pattern'),
    ('PA2','2nd Pattern'),
    ('PA3','3rd Pattern'),
    ('BA', 'Basics - Hands and Feet'),
    ('BW', 'Bag Work'),
    ('SP', 'Sparring'),
    ('BB', 'Board Breaking'),
    ('BF', 'Back and Fighting Stances'),
]

def rename_AssessmentUnitTypes(apps, schema_editor):
    AssessmentUnitType = apps.get_model('dashboard', 'AssessmentUnitType')
    a_units = dict(ASSESSMENT_UNITS)
    for aut in AssessmentUnitType.objects.all():
        aut.name = a_units[aut.name]
        aut.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0090_assessmentunit_unit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='assessmentunit',
            options={'ordering': ['unit__name']},
        ),
        migrations.RemoveField(
            model_name='assessmentunit',
            name='unitOLD',
        ),
        migrations.RunPython(rename_AssessmentUnitTypes)
    ]