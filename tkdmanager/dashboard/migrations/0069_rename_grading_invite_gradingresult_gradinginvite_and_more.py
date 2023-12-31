# Generated by Django 5.0 on 2024-01-04 15:15

from django.db import migrations, models

"""
def convert_forbelt_to_integer(apps, schema_editor):
    YourModel = apps.get_model('dashboard', 'GradingInvite')
    for instance in YourModel.objects.all():
        if instance.forbelt:
            instance.forbelt = int(instance.forbelt)
        else:
            instance.forbelt = 0
        instance.save()
    
    YourModel = apps.get_model('dashboard', 'GradingResult')
    for instance in YourModel.objects.all():
        if instance.forbelt:
            instance.forbelt = int(instance.forbelt)
        else:
            instance.forbelt = 0
        instance.save()

    YourModel = apps.get_model('dashboard', 'Member')
    for instance in YourModel.objects.all():
        if instance.belt:
            instance.belt = int(instance.belt)
        else:
            instance.belt = 0
        instance.save()
"""

class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0068_alter_member_options'),
    ]

    operations = [
#       migrations.RunPython(convert_forbelt_to_integer),
#        migrations.RenameField(
#            model_name='gradingresult',
#            old_name='grading_invite',
#            new_name='gradinginvite',
#        ),
        migrations.AlterField(
            model_name='gradinginvite',
            name='forbelt',
            field=models.IntegerField(verbose_name='For Belt'),
        ),
        migrations.AlterField(
            model_name='gradingresult',
            name='forbelt',
            field=models.IntegerField(verbose_name='For Belt'),
        ),
        migrations.AlterField(
            model_name='member',
            name='belt',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='member',
            name='idnumber',
            field=models.SmallIntegerField(unique=True, verbose_name='ID Number'),
        ),
    ]
