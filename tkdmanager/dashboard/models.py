from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Count
from django.urls import \
    reverse  # Used to generate URLs by reversing the URL patterns
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

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

def has_duplicate_styles(queryset):
    print(f'Input QS: {queryset.values()}')
    # Annotate the queryset to count occurrences of each style
    queryset = queryset.values('style__pk').annotate(style_count=Count('style__pk'))
    print(f'Annotated QS: {queryset.values()}')
    # Filter to get styles with count greater than 1
    duplicate_styles = queryset.filter(style_count__gt=1)
    print(f'Duplicated styles: {duplicate_styles.values()}')
    print(f'Exists? {duplicate_styles.exists()}')
    # Return True if there are duplicate styles, False otherwise
    return duplicate_styles.exists()

class NoLongerWorks(Exception):
    """
    A 'gentle' reminder that this thing doesn't work anymore
    """
    def __init__(self, message='This doesn\'t work anymore!'):
        self.message = message
        super().__init__(message)

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
    degree = models.IntegerField()
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['-style', '-degree']

    @classmethod
    def get_default_pk(cls):
        belt, created = cls.objects.get_or_create(
            style=Style.objects.get_or_create(name='TKD'),
            degree=2,
            name='No Belt'
        )
        return belt.pk
    
    def save(self, *args, **kwargs):
        """
        There can only be one belt with each degree for each style
        """
        # get all belts
        belts = Belt.objects.all()
        belt = belts.filter(style__pk=self.style.pk).filter(degree__exact=self.degree) # filter them to find ones with the same style and degree
        # see if there is already a belt in the same style with the same degree - if there is, scream
        if belt.exists():
            # This below line will render error by breaking page, you will see
            raise ValidationError(
                "The degree of a belt must be unique within its style"
            )
        return super(Belt, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.style}: {self.name}'
    
class Award(models.Model):
    """Model representing a type of award."""
    name = models.CharField(max_length=200)
    style = models.ForeignKey(Style, on_delete=models.PROTECT, default=Style.get_default_pk)

    def __str__(self):
        """string for representing the award"""
        return f'{self.style}: {self.name}' 
    
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
    belts = models.ManyToManyField(Belt, default=Belt.get_default_pk, related_name='belts')
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    team_leader_instructor = models.CharField(max_length=2, choices=TL_INST_RANKS, blank=True, verbose_name="Team Leader/Instructor")
    active = models.BooleanField(default=True)
    properties = models.ManyToManyField('MemberProperty', related_name='properties', blank=True)

    class Meta:
        ordering = ['last_name']

    def __str__(self):
        return f'{self.last_name}, {self.first_name} ({self.idnumber})'
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this member."""
        return reverse('dash-member-detail', args=[str(self.id)])

    def get_class_types_pretty(self):
        today = timezone.now().date()
        six_months_ago = today - timedelta(days=6 * 30)
        class_types = set(obj.get_type_display() for obj in self.students2classes.filter(date__gte=six_months_ago))
        return class_types
    
    def get_class_types(self):
        today = timezone.now().date()
        six_months_ago = today - timedelta(days=6 * 30)
        classes_queryset = self.students2classes.filter(date__gte=six_months_ago)
        class_types = classes_queryset.values_list('type', flat=True).distinct()
        return class_types
    
    def save(self, *args, **kwargs):
        """
        There can only be one belt with each style for a member
        """
        # get all belts
        belts = self.belts.all()
        print(f'Member Belts: {belts.values()}')
        # see if there is already a belt in the same style with the same degree - if there is, scream
        if has_duplicate_styles(belts):
            # This below line will render error by breaking page, you will see
            raise ValidationError(
                "A member can't have two belts from the same style!"
            )
        return super(Member, self).save(*args, **kwargs)
    
    @property
    def belt(self):
        """
        NOOO!
        """
        raise NoLongerWorks('You can\'t just read a belt from a member - specify a style and use get_belt(style)')
    
    def get_belt(self, style):
        """
        Return a belt from a given member and style
        """
        return self.belts.filter(style=style)
    
    def get_belt_context(self, context):
        """
        Use the context dict from a view to extract the style
        """
        style = context.request.session.get('style', 1)

        return self.get_belt(Style.objects.get(pk=style))

    @belt.setter
    def belt(self, new_belt):
        """
        when setting a belt
        see if we have any others on this guy of the same style
        if we do, replace them, else just add them
        """
        belts = self.belts
        existing_belt = belts.filter(style=new_belt.style)
        if existing_belt.exists():
            belts.remove(existing_belt)
        belts.add(new_belt)
        self.save()
    
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
    grading_type = models.ForeignKey('GradingType', on_delete=models.PROTECT, null=True)

    class Meta:
        ordering = ['-grading_datetime', 'grading_type']

    def get_grading_type_display(self):
        return self.grading_type.name

    def __str__(self):
        return f'{self.grading_type.style} Grading: {self.get_grading_type_display()} on {self.grading_datetime.strftime("%d/%m/%Y")}'
    
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
    style = models.ForeignKey(Style, on_delete=models.PROTECT, blank=True, null=True)
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
    style = models.ForeignKey(Style, on_delete=models.PROTECT, blank=True, null=True)
    teacher_property = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        """
        There can only be one type with the teacher_property attr set to true
        """
        # get all memberpropertytypes
        mpts = MemberPropertyType.objects.all()
        mpts = mpts.filter(style__pk=self.style.pk) # filter them to find ones with the same style
        teacherpropertyexists = mpts.filter(teacher_property__exact=True).exists() # see if there is a teacher propertytype in the style's memberpropertytypes
        if teacherpropertyexists:
            # This below line will render error by breaking page, you will see
            raise ValidationError(
                "There must only be one teacher propertytype for each style!"
            )
        return super(MemberPropertyType, self).save(*args, **kwargs)

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
    


