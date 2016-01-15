from django import forms

from .models import Splendid


class SplendidForm(forms.ModelForm):

    class Meta:
        model = Splendid
        fields = ('pack_name', 'creator', 'images_per_card', 'words', 'image_zip_file', 'source_of_images',)


