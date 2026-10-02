from django import forms 
from .models import *

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = '__all__'
        
class ApartmentFrom(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = '__all__'
         
class InquiryFrom(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = '__all__'
        
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['apartment'].queryset = Apartment.objects.filter(
            is_active=True
        ).exclude(status='sold')

    def clean_apartment(self):
        apartment = self.cleaned_data['apartment']
        active_bookings = Booking.objects.filter(
            apartment=apartment,
            status__in=['pending','confirmed'],
        )

        if self.instance.pk:
            active_bookings = active_bookings.exclude(pk=self.instance.pk)

        if active_bookings.exists():
            raise forms.ValidationError('Ин квартира аллакай брон шудааст')

        return apartment
        
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'apartment',
            'buyer',
            'buyer_name',
            'buyer_phone',
            'final_price',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['apartment'].queryset = Apartment.objects.filter(
            is_active=True
        ).exclude(status='sold').exclude(sale__isnull=False)
    
