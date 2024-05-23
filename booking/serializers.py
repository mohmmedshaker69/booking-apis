from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Payment, PaymentMethod, Booking, Flight, CarRental, Hotel, Taxi


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [ 'city', 'state', 'country', 'address','image']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User    
        fields = ['id', 'username','password']

    def create(self, validated_data):
        image = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, **image)
        return user

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'


class CarRentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarRental
        fields = '__all__'

class TaxiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxi
        fields = '__all__'

class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'



class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'seats', 'booking_date', 'check_in_date',
            'check_out_date', 'start_date', 'end_date', 'status',
            'content_type', 'object_id', 'content_object', 'total_price'
        ]

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name']

class PaymentSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Payment
        fields = ['id', 'booking', 'method', 'user', 'date', 'total_price']


class MultiModelSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        if isinstance(instance, Flight):
            serializer = FlightSerializer(instance)
        elif isinstance(instance, Hotel):
            serializer = HotelSerializer(instance)
        elif isinstance(instance, CarRental):
            serializer = CarRentalSerializer(instance)
        else:
            raise Exception("Unexpected type of instance")

        return serializer.data