# Generated by Django 4.1.4 on 2023-12-27 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0037_alter_class_options_alter_class_type_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.AlterField(
            model_name='assessmentunit',
            name='grading_result',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboard.gradingresult', verbose_name='Associated Grading Result'),
        ),
        migrations.AlterField(
            model_name='gradingresult',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member2gradings', to='dashboard.member'),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField()),
                ('due', models.DateTimeField()),
                ('paid', models.DateTimeField(blank=True)),
                ('member', models.ForeignKey(help_text='Who need to pay this?', on_delete=django.db.models.deletion.PROTECT, to='dashboard.member')),
                ('paymenttype', models.ForeignKey(help_text='What type of payment is this?', null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboard.paymenttype')),
            ],
            options={
                'ordering': ['-due', 'paymenttype'],
            },
        ),
    ]
