from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Flight)
admin.site.register(CarRental)
admin.site.register(Hotel)
admin.site.register(Taxi)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(PaymentMethod)
admin.site.register(Rating)