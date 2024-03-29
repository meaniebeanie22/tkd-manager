# Generated by Django 5.0.1 on 2024-02-14 09:51

import django.db.models.deletion
from django.db import migrations, models
from django.shortcuts import get_object_or_404

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

def make_placeholder_unittypes(apps, schema_editor):
    AssessmentUnitType = apps.get_model('dashboard', 'AssessmentUnitType')
    for dbname, vname in ASSESSMENT_UNITS:
        AssessmentUnitType.objects.create(name=dbname)

def copy_across_unitOLD(apps, schema_editor):
    AssessmentUnitType = apps.get_model('dashboard', 'AssessmentUnitType')
    AssessmentUnit = apps.get_model('dashboard', 'AssessmentUnit')

    for au in AssessmentUnit.objects.all():
        unitOLD = au.unitOLD
        au.unit = get_object_or_404(AssessmentUnitType, name=unitOLD)
        au.save()

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0089_alter_assessmentunit_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessmentunit',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.assessmentunittype'),
        ),
        migrations.RunPython(make_placeholder_unittypes),
        migrations.RunPython(copy_across_unitOLD)
    ]
