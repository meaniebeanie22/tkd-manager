from django.db import models
from django.urls import reverse # Used to generate URLs by reversing the URL patterns
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User

# Create your models here.

BELT_CHOICES = [
                ("White",      (('0', 'White Belt'), ('1', 'White ½'), ('2', 'White 1'), ('3', 'White 1 ½'), ('4', 'White 2'), ('5', 'White 2 ½'), ('6', 'White 3'), ('7', 'White-Orange'))),
                ("Orange",     (('8', 'Orange Belt'), ('9', 'Orange ½'), ('10', 'Orange 1'), ('11', 'Orange 1 ½'), ('12', 'Orange 2'), ('13', 'Orange 2 ½'), ('14', 'Orange 3'), ('15', 'White-Yellow'))),
                ("Yellow",     (('16', 'Yellow Belt'), ('17', 'Yellow ½'), ('18', 'Yellow 1'), ('19', 'Yellow 1 ½'), ('20', 'Yellow 2'), ('21', 'Yellow 2 ½'), ('22', 'Yellow 3'), ('23', 'White-Blue'))),
                ("Blue",       (('24', 'Blue Belt'), ('25', 'Blue ½'), ('26', 'Blue 1'), ('27', 'Blue 1 ½'), ('28', 'Blue 2'), ('29', 'Blue 2 ½'), ('30', 'Blue 3'), ('31', 'White-Red'))),
                ("Red",        (('32', 'Red Belt'), ('33', 'Red ½'), ('34', 'Red 1'), ('35', 'Red 1 ½'), ('36', 'Red 2'), ('37', 'Red 2 ½'), ('38', 'Red 3'))),
                ("Cho-Dan Bo", (('39', 'Cho-Dan Bo 1'), ('40', 'Cho-Dan Bo 2'), ('41', 'Cho-Dan Bo 3'), ('42', 'Cho-Dan Bo 4'), ('43', 'Cho-Dan Bo 5'), ('44', 'Cho-Dan Bo 6'), ('45', 'Advanced Cho-Dan Bo'), ('46', 'Probationary Black Belt'))),
                ("Black Belt", (('47', '1st Dan'), ('48', '2nd Dan'), ('49', '3rd Dan'), ('50', '4th Dan'), ('51', '5th Dan'), ('52', '6th Dan'), ('53', '7th Dan'), ('54', '8th Dan'), ('55', '9th Dan'))),
                ]

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

GRADINGS = [
    ('MS','Musketeers'),
    ('JR','Juniors'),
    ('SN','Seniors'),
    ('JS','Juniors/Seniors All'),
    ('JD','Juniors/Seniors Beginner-Blue'),
    ('JF','Juniors/Seniors Red-Black'),
    ('PA','TKD Patterns/Grading'),
    ('BB','Black Belt'),
    ('BJ','BJJ/MMA'),
    ('BO','Boxing'),
    ('BK','BJJ for Kids'),
    ('WE','Weapons'),
    ('FC','Fight Class'),
]

TL_INST_RANKS = [
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
]

#FDCC+BB+AA+
LETTER_GRADES = ['F', 'D', 'C', 'C+', 'B', 'B+', 'A', 'A+']

class Award(models.Model):
    """Model representing a type of award."""
    name = models.CharField(max_length=200)

    def __str__(self):
        """string for representing the award"""
        return self.name 
    
    def get_absolute_url(self):
        return reverse('award-detail', args=[str(self.id)])

class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    idnumber = models.SmallIntegerField(verbose_name="ID Number")
    address_line_1 = models.CharField(max_length=200, help_text="Unit, Street Number and Name", blank=True)
    address_line_2 = models.CharField(max_length=200, help_text="Suburb", blank=True)
    address_line_3 = models.CharField(max_length=4, help_text="Postcode", blank=True)
    date_of_birth = models.DateField()
    belt = models.CharField(max_length=50, choices=BELT_CHOICES, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    team_leader_instructor = models.CharField(max_length=2, choices=TL_INST_RANKS, blank=True, verbose_name="Team Leader/Instructor")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-belt','idnumber']

    def __str__(self):
        return f'{self.last_name}, {self.first_name} ({self.idnumber})'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member."""
        return reverse('member-detail', args=[str(self.id)])

    def get_class_types_pretty(self):
        today = datetime.now().date()
        six_months_ago = today - timedelta(days=6 * 30)
        class_types = set(obj.get_type_display() for obj in self.students2classes.filter(date__gte=six_months_ago))
        return class_types
    
    def get_class_types(self):
        today = datetime.now().date()
        six_months_ago = today - timedelta(days=6 * 30)
        classes_queryset = self.students2classes.filter(date__gte=six_months_ago)
        class_types = classes_queryset.values_list('type', flat=True).distinct()
        return class_types
    
class AssessmentUnit(models.Model):
    """An individual assessment component from one persons grading"""
    unit = models.CharField(max_length=200, choices=ASSESSMENT_UNITS)
    achieved_pts = models.SmallIntegerField()
    max_pts = models.SmallIntegerField() # if letter rep then should be set to 7
    grading_result = models.ForeignKey('GradingResult', on_delete=models.CASCADE, verbose_name="Associated Grading Result")

    class Meta:
        ordering = ['unit']
    
    def __str__(self):
        return f'{self.unit} - {self.grading_result}'
    
    def get_letter_rep(self):
        return LETTER_GRADES[self.achieved_pts]          

class GradingResult(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='member2gradings')
    date = models.DateField()
    type = models.CharField(max_length=2, choices=GRADINGS)
    assessor = models.ManyToManyField(Member, help_text='Who assessed this particular grading?', related_name='assessor2gradings')
    forbelt = models.CharField(max_length=50, choices=BELT_CHOICES, verbose_name="For Belt")
    comments = models.CharField(max_length=200, blank=True)
    award = models.ForeignKey(Award, on_delete=models.RESTRICT, verbose_name='Award', null=True, blank=True)
    is_letter = models.BooleanField(default=False)
    grading_invite = models.OneToOneField('GradingInvite', on_delete=models.CASCADE, null=True)
    
    class Meta:
        ordering = ['-date', 'type', '-forbelt', 'member__idnumber']

    def __str__(self):
        return f'{self.type} - {self.date}, by {self.member}'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member's grading results."""
        return reverse('grading-result-detail', args=[str(self.id)]) 
    
class GradingInvite(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    forbelt = models.CharField(max_length=50, choices=BELT_CHOICES, verbose_name="For Belt")
    type = models.CharField(max_length=2, choices=GRADINGS)
    date = models.DateField()
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.type} on {self.date} for {self.get_forbelt_display}, by {self.member}'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member's grading results."""
        return reverse('grading-invite-detail', args=[str(self.id)]) 

class Class(models.Model):
    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    type = models.CharField(max_length=2, choices=GRADINGS)
    instructors = models.ManyToManyField(Member, help_text='Who taught this class?', related_name='instructors2classes', blank=True)
    students = models.ManyToManyField(Member, help_text='Who attended this class?', related_name='students2classes', blank=True)

    class Meta:
        ordering = ['-date', '-start']

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member's grading results."""
        return reverse('class-detail', args=[str(self.id)]) 
    
    def __str__(self):
        return f'{self.get_type_display()}: {self.date.strftime("%x")}, {self.start.strftime("%X")} - {self.end.strftime("%X")}'

class Payment(models.Model):
    member = models.ForeignKey(Member, help_text='Who needs to pay this?', on_delete=models.PROTECT)
    paymenttype = models.ForeignKey('PaymentType', help_text='What type of payment is this?', null=True, on_delete=models.SET_NULL, verbose_name='Payment type')
    date_created = models.DateTimeField(default=timezone.now)
    date_due = models.DateTimeField()
    date_paid_in_full = models.DateTimeField(null=True, blank=True)
    amount_due = models.DecimalField(max_digits=7, decimal_places=2, help_text='Amount to be paid, in $', default=0)
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2, help_text='Amount currently paid, in $', default=0)

    class Meta:
        ordering = ['-date_due', 'paymenttype']

    def get_absolute_url(self):
        return reverse('payment-detail', args=[str(self.id)])
    
    def __str__(self):
        return f'{self.paymenttype} for {self.member}. Due {self.date_due.strftime("%x")}.'
    
    @property
    def is_past_due(self):
        return self.date_due < timezone.now()
    
    def get_payment_status(self):
        if self.is_past_due and self.date_paid_in_full == None:
            return "Overdue"
        elif self.date_paid_in_full:
            if self.date_paid_in_full > self.date_due:
                return "Paid Late"
            else:
                return "Paid On Time"
        else:
            return "Awaiting Payment"
        
class PaymentType(models.Model):
    name = models.CharField(max_length=200)
    standard_amount = models.DecimalField(max_digits=7, decimal_places=2, help_text='Standard amount to be paid, in $', default=0)

    def __str__(self):
        return f'{self.name}'
