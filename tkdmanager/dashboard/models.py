from django.db import models
from django.urls import reverse # Used to generate URLs by reversing the URL patterns
belt_id = {

}
# Create your models here.
class Belt(models.Model):
    """Model representing a belt."""
    BELTS = ['White', 'White 1/2', 'White 1', 'White 1 1/2', 'White 2', 'White 2 1/2', 'White 3', 'White-Orange', 'Orange', 'Orange 1/2', 'Orange 1', 'Orange 1 1/2', 'Orange 2', 'Orange 2 1/2', 'Orange 3', 'White-Yellow', 'Yellow', 'Yellow 1/2', 'Yellow 1', 'Yellow 1 1/2', 'Yellow 2', 'Yellow 2 1/2', 'Yellow 3', 'White-Blue', 'Blue', 'Blue 1/2', 'Blue 1', 'Blue 1 1/2', 'Blue 2', 'Blue 2 1/2', 'Blue 3', 'White-Red', 'Red', 'Red 1/2', 'Red 1', 'Red 1 1/2', 'Red 2', 'Red 2 1/2', 'Red 3', 'Cho-Dan Bo 1', 'Cho-Dan Bo 2', 'Cho-Dan Bo 3', 'Cho-Dan Bo 4', 'Cho-Dan Bo 5', 'Cho-Dan Bo 6', 'Advanced Cho-Dan Bo', 'Probationary Black Belt', '1st Dan', '2nd Dan', '3rd Dan', '4th Dan', '5th Dan', '6th Dan', '7th Dan', '8th Dan', '9th Dan']
    BELT_CHOICES = list(enumerate(BELTS)).append((None, 'No Belt'))
    belt = models.SmallIntegerField(
        choices=BELT_CHOICES,
    )
    def __str__(self):
        return self.belt
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('belt-detail', args=[str(self.id)])

class Award(models.Model):
    """Model representing an award."""
    recipients = models.ManyToManyField('Member', help_text='Who are the recipients of this award?')
    name = models.CharField('Type of Award', max_length=200, help_text="Enter what the award is for.")
    def __str__(self):
        """string for representing the award"""
        return self.name
    
    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('award-detail', args=[str(self.id)])
    
class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    def __str__(self):
        """String for representing the Model object."""
        return self.name