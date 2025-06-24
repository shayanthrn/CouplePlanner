from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register_user'),
    path('pair/', PairWithPartnerView.as_view(), name='pair_with_partner'),
    path('', HomeView.as_view(), name='home'),
    path('add/', AddActivityView.as_view(), name='add_activity'),
    path('activities/', ActivityQueueView.as_view(), name='activity_list'),
    path('activities/<int:pk>/accept/', AcceptActivityView.as_view(), name='accept_activity'),
    path('activities/<int:pk>/reject/', RejectActivityView.as_view(), name='reject_activity'),
    path('activity/<int:pk>/archive/', ArchiveActivityView.as_view(), name='archive_activity'),
    path('activity/<int:pk>/postpone/', PostponeActivityView.as_view(), name='postpone_activity'),
]
