from django.contrib.contenttypes.models import ContentType
from .models import Booking, Payment, PaymentMethod, Rating

def create_booking(user=None, model=None, object_id=None, seats=None,
                   start_date=None, end_date=None, check_in_date=None,
                   check_out_date=None):
    if not user or not model or not object_id:
        raise ValueError("User, model, and object_id are required")

    content_type = ContentType.objects.get_for_model(model)
    if not content_type:
        raise ValueError("Invalid model")

    booking = Booking.objects.create(
        user=user,
        seats=seats,
        start_date=start_date,
        end_date=end_date,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        status='Pending',
        content_type=content_type,
        object_id=object_id,
    )

    return booking

def add_rating(user, content_object, stars, comment):
    content_type = ContentType.objects.get_for_model(content_object)
    booking = Rating.objects.create(
        user=user,
        stars=stars,
        comment=comment,
        content_type=content_type,
        object_id=content_object.id,
        content_object=content_object
    )
    return booking

def create_payment(user, book, method_name):
    if not user or not book or not method_name:
        raise ValueError("User, book, and method_name are required")

    method = PaymentMethod.objects.filter(name=method_name).first()
    if not method:
        raise ValueError("Invalid method_name")

    payment = Payment.objects.create(
        user=user,
        booking=book,
        method=method,
    )
    return payment
