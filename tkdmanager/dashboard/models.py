from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models import F
from django.urls import \
    reverse  # Used to generate URLs by reversing the URL patterns
from django.utils import timezone

# Create your models here.
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

def time_in_a_month():
    return(timezone.now()+timedelta(days=30))

class Style(models.Model):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'
    
    @classmethod
    def get_default_pk(cls):
        style, created = cls.objects.get_or_create(
            name='TKD'
        )
        return style.pk

class Belt(models.Model):
    style = models.ForeignKey(Style, on_delete=models.PROTECT, default=Style.get_default_pk)
    degree = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['-degree']

    @classmethod
    def get_default_pk(cls):
        belt, created = cls.objects.get_or_create(
            degree=2,
            name='No Belt'
        )
        return belt.pk
    
    def __str__(self):
        return self.name
    
class Award(models.Model):
    """Model representing a type of award."""
    name = models.CharField(max_length=200)
    style = models.ForeignKey(Style, on_delete=models.PROTECT, default=Style.get_default_pk)

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
    belt = models.ForeignKey(Belt, default=Belt.get_default_pk, on_delete=models.PROTECT)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    team_leader_instructor = models.CharField(max_length=2, choices=TL_INST_RANKS, blank=True, verbose_name="Team Leader/Instructor")
    active = models.BooleanField(default=True)
    properties = models.ManyToManyField('MemberProperty', related_name='properties', blank=True)

    class Meta:
        ordering = ['-belt__degree','last_name']

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
    unit = models.ForeignKey('AssessmentUnitType', on_delete=models.SET_NULL, null=True)
    achieved_pts = models.SmallIntegerField()
    max_pts = models.SmallIntegerField() # if letter rep then should be set to 7
    grading_result = models.ForeignKey('GradingResult', on_delete=models.CASCADE, verbose_name="Associated Grading Result")

    class Meta:
        ordering = ['unit__name']
    
    def __str__(self):
        return f'{self.unit} - {self.grading_result}'
    
    def get_letter_rep(self):
        return LETTER_GRADES[self.achieved_pts]          

class Grading(models.Model):
    grading_datetime = models.DateTimeField(verbose_name="Grading Date & Time")
    style = models.ForeignKey(Style, on_delete=models.PROTECT, default=Style.get_default_pk)
    grading_type = models.ForeignKey('GradingType', on_delete=models.PROTECT, null=True)

    class Meta:
        ordering = ['-grading_datetime', 'grading_type']

    def get_grading_type_display(self):
        return self.grading_type.name

    def __str__(self):
        return f'Grading: {self.get_grading_type_display()} on {self.grading_datetime.strftime("%d/%m/%Y")}'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member's grading results."""
        return reverse('dash-grading-detail', args=[str(self.id)]) 

class GradingResult(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='member2gradings')
    assessor = models.ManyToManyField(Member, help_text='Who assessed this particular grading?', related_name='assessor2gradings')
    forbelt = models.ForeignKey(Belt, on_delete=models.PROTECT, default=Belt.get_default_pk, verbose_name="For Belt")
    comments = models.CharField(max_length=300, blank=True)
    award = models.ForeignKey(Award, on_delete=models.RESTRICT, verbose_name='Award', null=True, blank=True)
    is_letter = models.BooleanField(default=False)
    gradinginvite = models.OneToOneField('GradingInvite', on_delete=models.CASCADE, null=True, blank=True, verbose_name='Grading Invite')
    grading = models.ForeignKey(Grading, on_delete=models.SET_NULL, null=True)
    style = models.ForeignKey(Style, on_delete=models.PROTECT, default=Style.get_default_pk)
    
    class Meta:
        ordering = ['-grading__grading_datetime', '-forbelt', 'grading__grading_type', 'member__idnumber']

    def __str__(self):
        if self.grading:
            return f'GR: {self.grading.get_grading_type_display()} - {self.grading.grading_datetime.strftime("%d/%m/%Y")}, for {self.forbelt.name} by {self.member}'
        else:
            return f'GRADINGRESULT_NULL_GRADING by {self.member}'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member's grading results."""
        return reverse('dash-grading-result-detail', args=[str(self.id)]) 
    
class GradingInvite(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE,)
    forbelt = models.ForeignKey('Belt', on_delete=models.PROTECT, default=Belt.get_default_pk, verbose_name="For Belt")
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.OneToOneField('Payment', on_delete=models.SET_NULL, null=True, blank=True)
    grading = models.ForeignKey(Grading, on_delete=models.SET_NULL, null=True)
    style = models.ForeignKey(Style, on_delete=models.PROTECT, default=Style.get_default_pk)

    class Meta:
        ordering = ['-grading__grading_datetime', '-forbelt', 'grading__grading_type', 'member__idnumber']

    def __str__(self):
        if self.grading:
            return f'GI: {self.grading.get_grading_type_display()} on {self.grading.grading_datetime.strftime("%d/%m/%Y")} for {self.forbelt.name}, by {self.member}'
        else:
            return f'GRADINGINVITE_NULL_GRADING for {self.forbelt.name}, by {self.member}'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member's grading results."""
        return reverse('dash-grading-invite-detail', args=[str(self.id)]) 

class Class(models.Model):
    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    type = models.ForeignKey('ClassType', on_delete=models.PROTECT, null=True)
    instructors = models.ManyToManyField(Member, help_text='Who taught this class?', related_name='instructors2classes', blank=True)
    students = models.ManyToManyField(Member, help_text='Who attended this class?', related_name='students2classes', blank=True)

    class Meta:
        ordering = ['-date', '-start']
        verbose_name_plural = 'classes'

    def get_type_display(self):
        return self.type.name

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
    style = models.ForeignKey(Style, on_delete=models.PROTECT, default=Style.get_default_pk)
    name = models.CharField(max_length=200)
    standard_amount = models.DecimalField(max_digits=7, decimal_places=2, help_text='Standard amount to be paid, in $', default=0)

    def __str__(self):
        return f'{self.name}'
    
class RecurringPayment(models.Model):
    member = models.ForeignKey(Member, help_text='Who needs to pay this?', on_delete=models.PROTECT)
    payments = models.ManyToManyField(Payment, help_text='What payments are linked to this', blank=True)
    last_payment_date = models.DateField(null=True) # should be the same as the creation date of the most recent payment
    interval = models.DurationField(default=timedelta(days=30), help_text='DD HH:MM:SS')
    amount = models.DecimalField(max_digits=7, decimal_places=2, help_text='Amount to be paid, in $', default=0)
    next_due = models.GeneratedField(db_persist=True, output_field=models.DateTimeField(), expression=(F('last_payment_date') + F('interval')))
    paymenttype = models.ForeignKey(PaymentType, verbose_name='Payment Type', on_delete=models.PROTECT)
    
    class Meta:
            ordering = ['-next_due', 'paymenttype']

    def __str__(self):
        return f'Recurring Payment for {self.member}, ${self.amount} per {self.interval}'
    
    def get_absolute_url(self):
        return reverse('dash-rpayment-detail', args=[str(self.id)])

class MemberProperty(models.Model):
    class Meta:
        verbose_name_plural = 'member properties'
        ordering = ['name']

    # Team leader L3, or First Aid
    propertytype = models.ForeignKey('MemberPropertyType', on_delete=models.CASCADE, verbose_name='Property Type')
    member = models.ManyToManyField(Member, through=Member.properties.through, related_name='members', blank=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.propertytype} - {self.name}'

class MemberPropertyType(models.Model):
    # Instructor level, or qualifications
    name = models.CharField(max_length=200)
    searchable = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name}'

class AssessmentUnitType(models.Model):
    name = models.CharField(max_length=200, unique=True)
    style = models.ForeignKey(Style, on_delete=models.PROTECT, default=Style.get_default_pk)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'AssessmentUnitType: {self.name}'
    
class ClassType(models.Model):
    name = models.CharField(max_length=200, unique=True)
    style = models.ForeignKey(Style, on_delete=models.PROTECT, default=Style.get_default_pk)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'ClassType: {self.name}'
    
class GradingType(models.Model):
    name = models.CharField(max_length=200, unique=True)
    style = models.ForeignKey(Style, on_delete=models.PROTECT, default=Style.get_default_pk)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'GradingType: {self.name}'
    


