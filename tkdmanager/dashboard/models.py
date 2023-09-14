from django.db import models
from django.urls import reverse # Used to generate URLs by reversing the URL patterns

# Create your models here.

BELT_CHOICES = (
                ("White",      (('0', 'White'), ('1', 'White 1/2'), ('2', 'White 1'), ('3', 'White 1 1/2'), ('4', 'White 2'), ('5', 'White 2 1/2'), ('6', 'White 3'), ('7', 'White-Orange'))),
                ("Orange",     (('8', 'Orange'), ('9', 'Orange 1/2'), ('10', 'Orange 1'), ('11', 'Orange 1 1/2'), ('12', 'Orange 2'), ('13', 'Orange 2 1/2'), ('14', 'Orange 3'), ('15', 'White-Yellow'))),
                ("Yellow",     (('16', 'Yellow'), ('17', 'Yellow 1/2'), ('18', 'Yellow 1'), ('19', 'Yellow 1 1/2'), ('20', 'Yellow 2'), ('21', 'Yellow 2 1/2'), ('22', 'Yellow 3'), ('23', 'White-Blue'))),
                ("Blue",       (('24', 'Blue'), ('25', 'Blue 1/2'), ('26', 'Blue 1'), ('27', 'Blue 1 1/2'), ('28', 'Blue 2'), ('29', 'Blue 2 1/2'), ('30', 'Blue 3'), ('31', 'White-Red'))),
                ("Red",        (('32', 'Red'), ('33', 'Red 1/2'), ('34', 'Red 1'), ('35', 'Red 1 1/2'), ('36', 'Red 2'), ('37', 'Red 2 1/2'), ('38', 'Red 3'))),
                ("Cho-Dan Bo", (('39', 'Cho-Dan Bo 1'), ('40', 'Cho-Dan Bo 2'), ('41', 'Cho-Dan Bo 3'), ('42', 'Cho-Dan Bo 4'), ('43', 'Cho-Dan Bo 5'), ('44', 'Cho-Dan Bo 6'), ('45', 'Advanced Cho-Dan Bo'), ('46', 'Probationary Black Belt'))),
                ("Black Belt", (('47', '1st Dan'), ('48', '2nd Dan'), ('49', '3rd Dan'), ('50', '4th Dan'), ('51', '5th Dan'), ('52', '6th Dan'), ('53', '7th Dan'), ('54', '8th Dan'), ('55', '9th Dan'))),
                )

ASSESSMENT_UNITS = (
    ('SD','Self Defense'),
    ('SE','Self Develop'),
    ('PA1','1st Pattern'),
    ('PA2','2nd Pattern'),
    ('PA3','3rd Pattern'),
    ('BA', 'Basics - Hands and Feet')
)

GRADINGS = (
    ('MS','Musketeers'),
    ('JR','Juniors'),
    ('SN','Seniors'),
    ('BB','Black Belt')
)

TL_INST_RANKS = (
    ('T1','Team Leader Level 1'),
    ('T2','Team Leader Level 2'),
    ('T3','Team Leader Level 3'),
    ('T4','Team Leader Level 4'),
    ('T5','Team Leader Level 5'),
    ('IT','Trainee Instructor'),
    ('IA','Assistant Instructor'),
    ('II','Instructor'),
    ('IS','Senior Instructor'),
    ('IH','Head Instructor')
)

class Award(models.Model):
    """Model representing a type of award."""
    name = models.CharField(max_length=200)

    def __str__(self):
        """string for representing the award"""
        return self.name 

class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    idnumber = models.SmallIntegerField(verbose_name="ID Number")
    address_line_1 = models.CharField(max_length=200, help_text="Street Number and Name", blank=True)
    address_line_2 = models.CharField(max_length=200, help_text="Suburb", blank=True)
    address_line_3 = models.CharField(max_length=4, help_text="Postcode", blank=True)
    date_of_birth = models.DateField()
    belt = models.CharField(max_length=50, choices=BELT_CHOICES, blank=True)
    awards = models.ManyToManyField(Award, help_text="What awards has this person recieved?", blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    team_leader_instructor = models.CharField(max_length=2, choices=TL_INST_RANKS, blank=True, verbose_name="Team Leader/Instructor")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['idnumber']

    def __str__(self):
        return f'{self.last_name}, {self.first_name} ({self.idnumber})'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member."""
        return reverse('member-detail', args=[str(self.id)]) 
    
class AssessmentUnit(models.Model):
    """An individual assessment component from one persons grading"""
    unit = models.CharField(max_length=200, choices=ASSESSMENT_UNITS)
    achieved_pts = models.SmallIntegerField()
    max_pts = models.SmallIntegerField()
    grading_result = models.ForeignKey('GradingResult', on_delete=models.RESTRICT)
    
    def __str__(self):
        return f'{self.unit} - {self.grading_result}'

class GradingResult(models.Model):
    member = models.ForeignKey(Member, on_delete=models.RESTRICT, related_name='member2gradings')
    date = models.DateField()
    type = models.CharField(max_length=2, choices=GRADINGS)
    assessor = models.ManyToManyField(Member, help_text='Who assessed this particular grading?', related_name='assessor2gradings')
    forbelt = models.CharField(max_length=50, choices=BELT_CHOICES, verbose_name="For Belt")
    comments = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f'{self.type} - {self.date}, by {self.member}'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member's grading results."""
        return reverse('grading-result-detail', args=[str(self.id)]) 

