from django import forms
from .utils import CATEGORIES




class CreateListing(forms.Form):

    title = forms.CharField(max_length=200, label="Listing Title", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Title"}), required=True)
    category = forms.ChoiceField(choices=CATEGORIES,label="Category", widget=forms.Select(attrs={"class": "form-control form-select"}), required=True)
    bid = forms.DecimalField(min_value=0,label="Listing Bid", widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "Bid"}), required=True)
    image_url = forms.URLField(label="Image URL", widget=forms.URLInput(attrs={"class": "form-control", "placeholder": "Image Url"}), required=False)
    description = forms.CharField(label="Listing Description", widget=forms.Textarea(attrs={"class": "form-control", "placeholder": "Listing Description"}), required=False)

class CommentForm(forms.Form):
    comment = forms.CharField(label="", widget=forms.Textarea(attrs={"class": "form-control", "placeholder": "Comment"}), required=True)