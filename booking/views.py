from django.shortcuts import render
from django.db import IntegrityError, transaction
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from notifications.signals import notify
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
import csv
from django.http import HttpResponse
from .models import *
from .serializers import *
from .helpers import create_booking, create_payment, add_rating
from django.db.models import Q, F, Value
from django.db.models.functions import Concat
from .permessions import IsStaffOrReadOnlyForAuthenticated
# Create your views here.

class RegisterView(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [IsStaffOrReadOnlyForAuthenticated]
    @action(detail=True, methods=['post'], url_name='book', url_path='book')
    def book(self, request, pk=None):
        try:
            flight = self.get_object()
            seats = request.data.get('seats')
            if not flight or not seats:
                return Response({'error': 'Flight or seats is missing'}, status=status.HTTP_400_BAD_REQUEST)
            booking = create_booking(user=request.user, model=flight, object_id=flight.id, seats=seats)
            return Response({'status': 'Booking created', 'booking_id': booking.id})
        except IntegrityError as e:
            return Response({'error': "integrity error"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    @action(detail=True, methods=['post'], url_name='pay', url_path='pay')
    def pay(self, request, pk=None):
        instance = self.get_object() # filght
        method_name = request.data.get('method')

        try:
            booking = Booking.objects.get(content_type=ContentType.objects.get_for_model(Flight), object_id=instance.id, user=request.user)
            print(f"user={request.user},book= {booking}, method_name={method_name}")
            payment = create_payment(user=request.user,book= booking, method_name=method_name)
            return Response({'status': 'Payment created', 'payment_id': payment.id})
        except Booking.DoesNotExist:
            return Response({'status': 'Booking not found'}, status=404)
        except PaymentMethod.DoesNotExist:
            return Response({'status': 'Payment method not found'}, status=404)
        except Exception as e:
            return Response({'status': 'Error', 'message': str(e)}, status=500)



    @action(detail=True, methods=['post'], url_name='rate', url_path='rate')
    def rate(self, request, pk=None):
        object = self.get_object()
        stars = request.data.get('stars')
        comment = request.data.get('comment')
        rating = add_rating(request.user, object, stars, comment)
        return Response({'status': 'Rating added', 'rating_id': rating.id})


    
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsStaffOrReadOnlyForAuthenticated]

    @action(detail=True, methods=['post'], url_name='pay', url_path='pay')
    def pay(self, request, pk=None):
        book = self.get_object()
        if not book:
            return Response({'error': 'Booking object not found'}, status=status.HTTP_400_BAD_REQUEST)
        method = request.data.get('method')
        if not method:
            return Response({'error': 'Method is missing'}, status=status.HTTP_400_BAD_REQUEST)
        pay = create_payment(request.user, book, method)

        return Response({'status': 'Payment created', 'pay_id': pay.id})

class HotelViewSet(viewsets.ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [IsStaffOrReadOnlyForAuthenticated]


    @action(detail=True, methods=['post'], url_name='book', url_path='book')
    def book(self, request, pk=None):
        try:
            hotel = self.get_object()
            check_in_date = request.data.get('check_in_date')
            check_out_date = request.data.get('check_out_date')
            if not hotel or not check_in_date:
                return Response({'error': 'Flight or seats is missing'}, status=status.HTTP_400_BAD_REQUEST)
            booking = create_booking(user=request.user, model=hotel, object_id=hotel.id, check_in_date=check_in_date, check_out_date=check_out_date)
            return Response({'status': 'Booking created', 'booking_id': booking.id})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @action(detail=True, methods=['post'], url_name='pay', url_path='pay')
    def pay(self, request, pk=None):
        instance = self.get_object() 
        method_name = request.data.get('method')

        try:
            booking = Booking.objects.get(content_type=ContentType.objects.get_for_model(Hotel), object_id=instance.id)
            print(f"user={request.user},book= {booking}, method_name={method_name}")
            payment = create_payment(user=request.user,book= booking, method_name=method_name)
            return Response({'status': 'Payment created', 'payment_id': payment.id})
        except Booking.DoesNotExist:
            return Response({'status': 'Booking not found'}, status=404)
        except PaymentMethod.DoesNotExist:
            return Response({'status': 'Payment method not found'}, status=404)
        except Exception as e:
            return Response({'status': 'Error', 'message': str(e)}, status=500)


    @action(detail=True, methods=['post'], url_name='rate', url_path='rate')
    def rate(self, request, pk=None):
        object = self.get_object()
        stars = request.data.get('stars')
        comment = request.data.get('comment')
        rating = add_rating(request.user, object, stars, comment)
        return Response({'status': 'Rating added', 'rating_id': rating.id})

class CarRentalViewSet(viewsets.ModelViewSet):
    queryset = CarRental.objects.all()
    serializer_class = CarRentalSerializer
    permission_classes = [IsStaffOrReadOnlyForAuthenticated]


    @action(detail=True, methods=['post'], url_name='book', url_path='book')
    def book(self, request, pk=None):
        try:
            hotel = self.get_object()
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            if not hotel or not start_date:
                return Response({'error': 'car or seats is missing'}, status=status.HTTP_400_BAD_REQUEST)
            booking = create_booking(user=request.user, model=hotel, object_id=hotel.id, start_date=start_date, end_date=end_date)
            return Response({'status': 'Booking created', 'booking_id': booking.id})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=True, methods=['post'], url_name='pay', url_path='pay')
    def pay(self, request, pk=None):
        instance = self.get_object() 
        method_name = request.data.get('method')

        try:
            booking = Booking.objects.get(content_type=ContentType.objects.get_for_model(CarRental), object_id=instance.id, user=request.user)
            print(f"user={request.user},book= {booking}, method_name={method_name}")
            payment = create_payment(user=request.user,book= booking, method_name=method_name)
            return Response({'status': 'Payment created', 'payment_id': payment.id})
        except Booking.DoesNotExist:
            return Response({'status': 'Booking not found'}, status=404)
        except PaymentMethod.DoesNotExist:
            return Response({'status': 'Payment method not found'}, status=404)
        except Exception as e:
            return Response({'status': 'Error', 'message': str(e)}, status=500)


    @action(detail=True, methods=['post'], url_name='rate', url_path='rate')
    def rate(self, request, pk=None):
        object = self.get_object()
        stars = request.data.get('stars')
        comment = request.data.get('comment')
        rating = add_rating(request.user, object, stars, comment)
        return Response({'status': 'Rating added', 'rating_id': rating.id})
    
class TaxiViewSet(viewsets.ModelViewSet):
    queryset = Taxi.objects.all()
    serializer_class = TaxiSerializer
    permission_classes = [IsStaffOrReadOnlyForAuthenticated]

    @action(detail=True, methods=['post'], url_name='rate', url_path='rate')
    def rate(self, request, pk=None):
        object = self.get_object()
        stars = request.data.get('stars')
        comment = request.data.get('comment')
        rating = add_rating(request.user, object, stars, comment)
        return Response({'status': 'Rating added', 'rating_id': rating.id})

class SearchFlight(ListAPIView):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        'take_off_country', 'take_off_city', 'take_off_airport',
        'landing_country', 'landing_city', 'landing_airport',
        'plane_model', 'price', 'date', 'take_off_time', 'landing_time'
    ]
    permission_classes = [IsAuthenticated]


class SearchHotel(ListAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'address', 'stars', 'price']
    permission_classes = [IsAuthenticated]


class SearchCarRental(ListAPIView):
    queryset = CarRental.objects.all()
    serializer_class = CarRentalSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['company', 'car_model', 'price']
    permission_classes = [IsAuthenticated]
