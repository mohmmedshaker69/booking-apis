from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.username} Profile'



class Flight(models.Model):
    take_off_country = models.CharField(max_length=100)
    take_off_city = models.CharField(max_length=100)
    take_off_airport = models.CharField(max_length=100)
    landing_country = models.CharField(max_length=100)
    landing_city = models.CharField(max_length=100)
    landing_airport = models.CharField(max_length=100)
    date = models.DateField()
    bording = models.TimeField()
    take_off_time = models.TimeField()
    landing_time = models.TimeField()
    plane_model = models.CharField(max_length=200)
    price = models.FloatField()

    @property
    def duration(self):
        return self.landing_time - self.take_off_time

    def __str__(self):
        return f'{self.take_off_airport} to {self.landing_airport} on {self.date}'
    

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seats = models.IntegerField(null=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')],
        default='Pending'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
    
    @property
    def total_price(self):
        if self.seats and hasattr(self.content_object, 'price'):
            return self.content_object.price * self.seats
        
        if self.check_in_date and self.check_out_date and hasattr(self.content_object, 'price'):
            duration = (self.check_out_date - self.check_in_date).days
            return self.content_object.price * duration
        
        if self.start_date and self.end_date and hasattr(self.content_object, 'price'):
            duration = (self.end_date - self.start_date).days
            return self.content_object.price * duration
        
        return 0

    def __str__(self):
        return f'{self.user.username}'
    

class PaymentMethod(models.Model):
    name = models.CharField(
        max_length=100, 
        choices=[
            ('visa', 'Visa'), ('mastercard', 'Mastercard'),
            ('paypal', 'PayPal'), ('applepay', 'ApplePay'),
            ('googlepay', 'GooglePay')
            ]
        )

    def __str__(self):
        return self.name



class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.booking.total_price

    def __str__(self):
        return self.booking.content_object
    
class Rating(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,)
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    comment = models.TextField(null=True, blank=True) 
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        service = self.content_object
        return f"{self.stars} stars for {service} by {self.user}" if service else None
    
class CarRental(models.Model):
    company = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)


    def __str__(self):
        return f"Car rental from {self.company}"

class Hotel(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  
    stars = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=1)

    def __str__(self):
        return self.name
    
class Taxi(models.Model):
    company = models.CharField(max_length=100)
    car_model = models.CharField(max_length=100)
    pick_up_location = models.CharField(max_length=100)
    drop_off_location = models.CharField(max_length=100)
    pick_up_date = models.DateTimeField()
    drop_off_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    def __str__(self):
        return f"Taxi from {self.company}"