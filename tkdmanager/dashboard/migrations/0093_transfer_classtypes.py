import dashboard.models
import django.db.models.deletion
from django.db import migrations, models

GRADINGS = [
    ('MS','Musketeers'),
    ('JR','Juniors'),
    ('SN','Seniors'),
    ('JS','Juniors/Seniors All'),
    ('JD','Juniors/Seniors Beginner-Blue'),
    ('JF','Juniors/Seniors Red-Black'),
    ('PA','TKD Patterns/Grading'),
    ('BB','Black Belts'),
    ('BJ','BJJ/MMA'),
    ('BO','Boxing'),
    ('BK','BJJ for Kids'),
    ('WE','Weapons'),
    ('FC','Fight Class'),
]

def transferClasses(apps, schema_editor):
    ClassType = apps.get_model('dashboard', 'ClassType')
    Class = apps.get_model('dashboard', 'Class')

    for c in Class.objects.all():
        obj, created = ClassType.objects.get_or_create(name=c.type)
        c.classtype = obj
        c.save()

def renameClassTypes(apps, schema_editor):
    g_dict = dict(GRADINGS)
    ClassType = apps.get_model('dashboard', 'ClassType')

    for ct in ClassType.objects.all():
        ct.name = g_dict[ct.name]
        ct.save()

def transferGradings(apps, schema_editor):
    GradingType = apps.get_model('dashboard', 'GradingType')
    Grading = apps.get_model('dashboard', 'Grading')

    for g in Grading.objects.all():
        obj, created = GradingType.objects.get_or_create(name=g.grading_type)
        g.grading_typeNEW = obj
        g.save()

def renameGradingTypes(apps, schema_editor):
    g_dict = dict(GRADINGS)
    GradingType = apps.get_model('dashboard', 'GradingType')

    for gt in GradingType.objects.all():
        gt.name = g_dict[gt.name]
        gt.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0092_classtype_style_alter_assessmentunittype_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='grading',
            name='grading_typeNEW',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='dashboard.gradingtype'),
        ),
        migrations.RunPython(transferClasses),
        migrations.RunPython(transferGradings),
        migrations.RunPython(renameClassTypes),
        migrations.RunPython(renameGradingTypes)
    ]
