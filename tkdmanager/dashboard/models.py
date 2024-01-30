from django.db import models
from django.db.models import F
from django.urls import reverse # Used to generate URLs by reversing the URL patterns
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User

# Create your models here.

BELT_CHOICES = [
    (None, 'No Belt'), 
    ("White",      ((0, 'White Belt'), (1, 'White ½'), (2, 'White 1'), (3, 'White 1 ½'), (4, 'White 2'), (5, 'White 2 ½'), (6, 'White 3'), (7, 'White-Orange'))),
    ("Orange",     ((8, 'Orange Belt'), (9, 'Orange ½'), (10, 'Orange 1'), (11, 'Orange 1 ½'), (12, 'Orange 2'), (13, 'Orange 2 ½'), (14, 'Orange 3'), (15, 'White-Yellow'))),
    ("Yellow",     ((16, 'Yellow Belt'), (17, 'Yellow ½'), (18, 'Yellow 1'), (19, 'Yellow 1 ½'), (20, 'Yellow 2'), (21, 'Yellow 2 ½'), (22, 'Yellow 3'), (23, 'White-Blue'))),
    ("Blue",       ((24, 'Blue Belt'), (25, 'Blue ½'), (26, 'Blue 1'), (27, 'Blue 1 ½'), (28, 'Blue 2'), (29, 'Blue 2 ½'), (30, 'Blue 3'), (31, 'White-Red'))),
    ("Red",        ((32, 'Red Belt'), (33, 'Red ½'), (34, 'Red 1'), (35, 'Red 1 ½'), (36, 'Red 2'), (37, 'Red 2 ½'), (38, 'Red 3'))),
    ("Cho-Dan Bo", ((39, 'Cho-Dan Bo 1'), (40, 'Cho-Dan Bo 2'), (41, 'Cho-Dan Bo 3'), (42, 'Cho-Dan Bo 4'), (43, 'Cho-Dan Bo 5'), (44, 'Cho-Dan Bo 6'), (45, 'Advanced Cho-Dan Bo'), (46, 'Probationary Black Belt'))),
    ("Black Belt", ((47, '1st Dan'), (48, '2nd Dan'), (49, '3rd Dan'), (50, '4th Dan'), (51, '5th Dan'), (52, '6th Dan'), (53, '7th Dan'), (54, '8th Dan'), (55, '9th Dan'))),
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
    ('BB','Black Belts'),
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

def determine_belt_type(id):
    if id > 39: # is x id a blackbelt or not (for gradings)
        return 'Black'
    else:
        return 'Color'

def time_in_a_month():
    return(timezone.now()+timedelta(days=30))

class Award(models.Model):
    """Model representing a type of award."""
    name = models.CharField(max_length=200)

    def __str__(self):
        """string for representing the award"""
        return self.name 
    
    def get_absolute_url(self):
        return reverse('dash-award-detail', args=[str(self.id)])

class Member(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    idnumber = models.SmallIntegerField(verbose_name="ID Number", unique=True)
    address_line_1 = models.CharField(max_length=200, help_text="Unit, Street Number and Name", blank=True)
    address_line_2 = models.CharField(max_length=200, help_text="Suburb", blank=True)
    address_line_3 = models.CharField(max_length=4, help_text="Postcode", blank=True)
    date_of_birth = models.DateField()
    belt = models.IntegerField(choices=BELT_CHOICES, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    team_leader_instructor = models.CharField(max_length=2, choices=TL_INST_RANKS, blank=True, verbose_name="Team Leader/Instructor")
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-belt','last_name']

    def __str__(self):
        return f'{self.last_name}, {self.first_name} ({self.idnumber})'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member."""
        return reverse('dash-member-detail', args=[str(self.id)])

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

class Grading(models.Model):
    grading_type = models.CharField(max_length=2, choices=GRADINGS)
    grading_datetime = models.DateTimeField(verbose_name="Grading Date & Time")

    class Meta:
        ordering = ['-grading_datetime', 'grading_type']

    def __str__(self):
        return f'Grading: {self.get_grading_type_display()} on {self.grading_datetime.strftime("%d/%m/%Y")}'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member's grading results."""
        return reverse('dash-grading-detail', args=[str(self.id)]) 

class GradingResult(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='member2gradings')
    assessor = models.ManyToManyField(Member, help_text='Who assessed this particular grading?', related_name='assessor2gradings')
    forbelt = models.IntegerField(choices=BELT_CHOICES, verbose_name="For Belt")
    comments = models.CharField(max_length=300, blank=True)
    award = models.ForeignKey(Award, on_delete=models.RESTRICT, verbose_name='Award', null=True, blank=True)
    is_letter = models.BooleanField(default=False)
    gradinginvite = models.OneToOneField('GradingInvite', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Grading Invite')
    grading = models.ForeignKey(Grading, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-grading__grading_datetime', '-forbelt', 'grading__grading_type', 'member__idnumber']

    def __str__(self):
        if self.grading:
            return f'GR: {self.grading.get_grading_type_display()} - {self.grading.grading_datetime.strftime("%d/%m/%Y")}, by {self.member}'
        else:
            return f'GRADINGRESULT_NULL_GRADING by {self.member}'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member's grading results."""
        return reverse('dash-grading-result-detail', args=[str(self.id)]) 
    
class GradingInvite(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE,)
    forbelt = models.IntegerField(choices=BELT_CHOICES, verbose_name="For Belt")
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.OneToOneField('Payment', on_delete=models.SET_NULL, null=True, blank=True)
    grading = models.ForeignKey(Grading, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-grading__grading_datetime', '-forbelt', 'grading__grading_type', 'member__idnumber']

    def __str__(self):
        if self.grading:
            return f'GI: {self.grading.get_grading_type_display()} on {self.grading.grading_datetime.strftime("%d/%m/%Y")} for {self.get_forbelt_display()}, by {self.member}'
        else:
            return f'GRADINGINVITE_NULL_GRADING for {self.get_forbelt_display()}, by {self.member}'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member's grading results."""
        return reverse('dash-grading-invite-detail', args=[str(self.id)]) 

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
        return reverse('dash-class-detail', args=[str(self.id)]) 
    
    def __str__(self):
        return f'{self.get_type_display()}: {self.date.strftime("%d/%m/%Y")}, {self.start.strftime("%X")} - {self.end.strftime("%X")}'

class Payment(models.Model):
    member = models.ForeignKey(Member, help_text='Who needs to pay this?', on_delete=models.PROTECT)
    paymenttype = models.ForeignKey('PaymentType', help_text='What type of payment is this?', null=True, on_delete=models.SET_NULL, verbose_name='Payment type')
    date_created = models.DateTimeField(default=timezone.now)
    date_due = models.DateTimeField(default=time_in_a_month)
    date_paid_in_full = models.DateTimeField(null=True, blank=True)
    amount_due = models.DecimalField(max_digits=7, decimal_places=2, help_text='Amount to be paid, in $', default=0)
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2, help_text='Amount currently paid, in $', default=0)

    class Meta:
        ordering = ['-date_due', 'paymenttype']

    def get_absolute_url(self):
        return reverse('dash-payment-detail', args=[str(self.id)])
    
    def __str__(self):
        return f'{self.paymenttype} for {self.member}. Due {self.date_due.strftime("%d/%m/%Y")}.'
    
    @property
    def is_past_due(self):
        return self.date_due < timezone.now()
    
    @property
    def payment_status(self):
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
    
class RecurringPayment(models.Model):
    member = models.ForeignKey(Member, help_text='Who needs to pay this?', on_delete=models.PROTECT)
    payments = models.ManyToManyField(Payment, help_text='What payments are linked to this', blank=True)
    last_payment_date = models.DateField(default=timezone.now) # should be the same as the creation date of the most recent payment
    interval = models.DurationField(default=timedelta(days=30))
    amount = models.DecimalField(max_digits=7, decimal_places=2, help_text='Amount to be paid, in $', default=0)
    next_due = models.GeneratedField(db_persist=True, output_field=models.DateTimeField(), expression=(F('last_payment_date') + F('interval')))
    paymenttype = models.ForeignKey(PaymentType, help_text='Payment Type', on_delete=models.PROTECT)

    def __str__(self):
        return f'Recurring Payment for {self.member}, ${self.amount} per {self.interval}'
