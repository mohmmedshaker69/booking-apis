from django.urls import path, include, re_path
import notifications.urls
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register('flight', views.FlightViewSet)
router.register('booking', views.BookingViewSet)
router.register('car_rental', views.CarRentalViewSet)
router.register('hotel', views.HotelViewSet)
router.register('taxi', views.TaxiViewSet)




urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('search_flight/', views.SearchFlight.as_view(), name='search'),
    path('search_hotel/', views.SearchHotel.as_view(), name='search_hotel'),
    path('search_car_rental/', views.SearchCarRental.as_view(), name='search_car_rental'),
    re_path(r'^inbox/notifications/', include((notifications.urls, 'notifications'), namespace='notifications')),


]