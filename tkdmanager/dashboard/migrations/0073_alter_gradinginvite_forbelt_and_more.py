# Generated by Django 5.0 on 2024-01-03 16:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0072_alter_member_belt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gradinginvite',
            name='forbelt',
            field=models.CharField(choices=[('White', [(0, 'White Belt'), (1, 'White ½'), (2, 'White 1'), (3, 'White 1 ½'), (4, 'White 2'), (5, 'White 2 ½'), (6, 'White 3'), (7, 'White-Orange')]), ('Orange', [(8, 'Orange Belt'), (9, 'Orange ½'), (10, 'Orange 1'), (11, 'Orange 1 ½'), (12, 'Orange 2'), (13, 'Orange 2 ½'), (14, 'Orange 3'), (15, 'White-Yellow')]), ('Yellow', [(16, 'Yellow Belt'), (17, 'Yellow ½'), (18, 'Yellow 1'), (19, 'Yellow 1 ½'), (20, 'Yellow 2'), (21, 'Yellow 2 ½'), (22, 'Yellow 3'), (23, 'White-Blue')]), ('Blue', [(24, 'Blue Belt'), (25, 'Blue ½'), (26, 'Blue 1'), (27, 'Blue 1 ½'), (28, 'Blue 2'), (29, 'Blue 2 ½'), (30, 'Blue 3'), (31, 'White-Red')]), ('Red', [(32, 'Red Belt'), (33, 'Red ½'), (34, 'Red 1'), (35, 'Red 1 ½'), (36, 'Red 2'), (37, 'Red 2 ½'), (38, 'Red 3')]), ('Cho-Dan Bo', [(39, 'Cho-Dan Bo 1'), (40, 'Cho-Dan Bo 2'), (41, 'Cho-Dan Bo 3'), (42, 'Cho-Dan Bo 4'), (43, 'Cho-Dan Bo 5'), (44, 'Cho-Dan Bo 6'), (45, 'Advanced Cho-Dan Bo'), (46, 'Probationary Black Belt')]), ('Black Belt', [(47, '1st Dan'), (48, '2nd Dan'), (49, '3rd Dan'), (50, '4th Dan'), (51, '5th Dan'), (52, '6th Dan'), (53, '7th Dan'), (54, '8th Dan'), (55, '9th Dan')])], max_length=50, verbose_name='For Belt'),
        ),
        migrations.AlterField(
            model_name='gradingresult',
            name='forbelt',
            field=models.CharField(choices=[('White', [(0, 'White Belt'), (1, 'White ½'), (2, 'White 1'), (3, 'White 1 ½'), (4, 'White 2'), (5, 'White 2 ½'), (6, 'White 3'), (7, 'White-Orange')]), ('Orange', [(8, 'Orange Belt'), (9, 'Orange ½'), (10, 'Orange 1'), (11, 'Orange 1 ½'), (12, 'Orange 2'), (13, 'Orange 2 ½'), (14, 'Orange 3'), (15, 'White-Yellow')]), ('Yellow', [(16, 'Yellow Belt'), (17, 'Yellow ½'), (18, 'Yellow 1'), (19, 'Yellow 1 ½'), (20, 'Yellow 2'), (21, 'Yellow 2 ½'), (22, 'Yellow 3'), (23, 'White-Blue')]), ('Blue', [(24, 'Blue Belt'), (25, 'Blue ½'), (26, 'Blue 1'), (27, 'Blue 1 ½'), (28, 'Blue 2'), (29, 'Blue 2 ½'), (30, 'Blue 3'), (31, 'White-Red')]), ('Red', [(32, 'Red Belt'), (33, 'Red ½'), (34, 'Red 1'), (35, 'Red 1 ½'), (36, 'Red 2'), (37, 'Red 2 ½'), (38, 'Red 3')]), ('Cho-Dan Bo', [(39, 'Cho-Dan Bo 1'), (40, 'Cho-Dan Bo 2'), (41, 'Cho-Dan Bo 3'), (42, 'Cho-Dan Bo 4'), (43, 'Cho-Dan Bo 5'), (44, 'Cho-Dan Bo 6'), (45, 'Advanced Cho-Dan Bo'), (46, 'Probationary Black Belt')]), ('Black Belt', [(47, '1st Dan'), (48, '2nd Dan'), (49, '3rd Dan'), (50, '4th Dan'), (51, '5th Dan'), (52, '6th Dan'), (53, '7th Dan'), (54, '8th Dan'), (55, '9th Dan')])], max_length=50, verbose_name='For Belt'),
        ),
        migrations.AlterField(
            model_name='member',
            name='belt',
            field=models.IntegerField(blank=True, choices=[('White', [(0, 'White Belt'), (1, 'White ½'), (2, 'White 1'), (3, 'White 1 ½'), (4, 'White 2'), (5, 'White 2 ½'), (6, 'White 3'), (7, 'White-Orange')]), ('Orange', [(8, 'Orange Belt'), (9, 'Orange ½'), (10, 'Orange 1'), (11, 'Orange 1 ½'), (12, 'Orange 2'), (13, 'Orange 2 ½'), (14, 'Orange 3'), (15, 'White-Yellow')]), ('Yellow', [(16, 'Yellow Belt'), (17, 'Yellow ½'), (18, 'Yellow 1'), (19, 'Yellow 1 ½'), (20, 'Yellow 2'), (21, 'Yellow 2 ½'), (22, 'Yellow 3'), (23, 'White-Blue')]), ('Blue', [(24, 'Blue Belt'), (25, 'Blue ½'), (26, 'Blue 1'), (27, 'Blue 1 ½'), (28, 'Blue 2'), (29, 'Blue 2 ½'), (30, 'Blue 3'), (31, 'White-Red')]), ('Red', [(32, 'Red Belt'), (33, 'Red ½'), (34, 'Red 1'), (35, 'Red 1 ½'), (36, 'Red 2'), (37, 'Red 2 ½'), (38, 'Red 3')]), ('Cho-Dan Bo', [(39, 'Cho-Dan Bo 1'), (40, 'Cho-Dan Bo 2'), (41, 'Cho-Dan Bo 3'), (42, 'Cho-Dan Bo 4'), (43, 'Cho-Dan Bo 5'), (44, 'Cho-Dan Bo 6'), (45, 'Advanced Cho-Dan Bo'), (46, 'Probationary Black Belt')]), ('Black Belt', [(47, '1st Dan'), (48, '2nd Dan'), (49, '3rd Dan'), (50, '4th Dan'), (51, '5th Dan'), (52, '6th Dan'), (53, '7th Dan'), (54, '8th Dan'), (55, '9th Dan')])]),
        ),
    ]
