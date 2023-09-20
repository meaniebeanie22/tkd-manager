from typing import Any
from django.forms import ModelForm
from .models import GradingResult
from django.core.exceptions import ValidationError

class GradingResultForm(ModelForm):
    def clean_belt(self):
        print('clean_belt run')
        belt = self.cleaned_data['belt']
        date = self.cleaned_data['date']
        member = self.cleaned_data['member']

        # check if this is higher than all prior gradings
        gradings = member.member2gradings.order_by('-date')
        prior_gradings = gradings.filter(date__lt=date).all()
        # if this is the most recent grading the person has had
        if date > gradings.first().date:
            # make sure their belt isnt higher than this grading is for
            if member.belt > belt:
                raise ValidationError('This member has a higher belt than what this grading for, and this grading is their most recent - ensure you add gradings from the most recent down.')
        
        # check that this grading is not for a lower belt than all of the past ones (same is alright - you can theoretically fail a grading)
        for g in prior_gradings:
            if g.belt > belt:
                raise ValidationError('Cannot demote through a grading - prior gradings are for a higher level!')
                break

        return belt

    class Meta:
        model = GradingResult
        fields = ['member','date','type','forbelt','assessor','comments','award']

"""
from django.db.models.signals import post_save

def update_belt(sender, **kwargs):
    target = kwargs['instance'].member # target should be a member
    target.belt = target.member2gradings.order_by('-date').first().forbelt
    target.save()

post_save.connect(update_belt, sender=GradingResult)

"""