from django.db import models

# Create your models here.

from django.core.validators import MinValueValidator, MaxValueValidator

PDFS = 'pdfs'

# Create your models here.

class Splendid(models.Model):
    pack_name = models.CharField(max_length=200, help_text='Name of you pack of cards, e.g. SplendidSigns')
    creator = models.CharField(max_length=20, help_text='Enter your twitter username to get a tweet when the pack has been created and is ready for download')
    images_per_card = models.IntegerField(validators=[MinValueValidator(3), MaxValueValidator(8)], help_text='Between 3 and 8 symbols per card')
    words = models.TextField(null=True, blank=True, help_text="A list of words seperated by a comma. To have more than one line use \\n as a return:<br/>e.g. Merci, S'il vous plaît, Au revoir, Ça va?\\nHow are you? ")
    image_zip_file = models.FileField(upload_to='zips', null=True, blank=True, help_text='A zip file containing images to be used on the cards. <br>A pack can consist of just words, just images from the zip file or a mixture of images and words.')
    source_of_images = models.TextField( null=True, blank=True, help_text='What are the orginas of your images. For examples where did you download them. <br/>e.g. Traffic signs images downloaded from https://www.gov.uk/traffic-sign-images.<br/>Traffic signs are Crown copyright and used under http://www.nationalarchives.gov.uk/doc/open-government-licence/')
    # No need for BooleanField as pdf will be null or point to error.pdf
    pdf = models.FileField(upload_to=PDFS, null=True, blank=True)
    pair_image = models.FileField(upload_to=PDFS, null=True, blank=True)
    free = models.BooleanField(default=True)


    # Date published ?

    def __str__(self): 
        return (self.pack_name + ". Created by " + self.creator)
