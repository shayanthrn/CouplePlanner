from django.shortcuts import redirect, get_object_or_404
from django.views import View
from .models import Activity, Couple, User
from django.views.generic import TemplateView, ListView
from django.views.generic.edit import FormView, CreateView
from django.contrib.auth import login
from django.urls import reverse_lazy
from .forms import UserRegistrationForm, CouplePairForm, ActivityForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from datetime import date, timedelta
from django.utils import timezone
from .utils import weighted_random_activity

class UserRegisterView(FormView):
    template_name = 'planner/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('pair_with_partner')

    def form_valid(self, form):
        user = form.save()  
        login(self.request, user)
        return super().form_valid(form)
    
class PairWithPartnerView(LoginRequiredMixin, FormView):
    template_name = 'planner/pair_with_partner.html'
    form_class = CouplePairForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        partner_email = form.cleaned_data['partner_email']
        user = self.request.user
        
        try:
            partner = User.objects.get(email=partner_email)
        except User.DoesNotExist:
            form.add_error('partner_email', 'No user found with that email.')
            return self.form_invalid(form)
        
        if partner == user:
            form.add_error('partner_email', "You can't pair with yourself.")
            return self.form_invalid(form)
        
        if Couple.objects.filter(user1__in=[user, partner]).exists() or Couple.objects.filter(user2__in=[user, partner]).exists():
            form.add_error('partner_email', "One of you is already paired.")
            return self.form_invalid(form)
        
        Couple.objects.create(user1=user, user2=partner)
        messages.success(self.request, "Couple created successfully!")
        return super().form_valid(form)

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'planner/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        couple = Couple.objects.filter(user1=user).first() or Couple.objects.filter(user2=user).first()
        context['couple'] = couple

        if not couple:
            context['activities'] = None
            context['suggested_activity'] = None
            return context

        pool_activities = couple.activities.filter(status='pool')

        context['activities'] = pool_activities.order_by('deadline')

        # Find last suggested activity for this week
        today = date.today()
        week_start = today - timedelta(days=today.weekday())  # Monday
        week_end = week_start + timedelta(days=6)

        last_suggested = pool_activities.filter(
            last_suggested__gte=week_start,
            last_suggested__lte=week_end,
        ).first()

        if last_suggested:
            suggested = last_suggested
        else:
            suggested = weighted_random_activity(pool_activities)
            if suggested:
                suggested.last_suggested = today
                suggested.save(update_fields=['last_suggested'])

        context['suggested_activity'] = suggested
        return context
    
class AddActivityView(LoginRequiredMixin, CreateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'planner/add_activity.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = self.request.user
        couple = Couple.objects.filter(user1=user).first() or Couple.objects.filter(user2=user).first()
        if not couple:
            messages.error(self.request, "You must be paired with a partner to add an activity.")
            return redirect('pair_with_partner')

        activity = form.save(commit=False)
        activity.couple = couple
        activity.added_by = user
        activity.status = 'queued'
        activity.save()

        messages.success(self.request, "Activity added to queue.")
        return super().form_valid(form)
    
class ActivityQueueView(LoginRequiredMixin, ListView):
    model = Activity
    template_name = 'planner/activity_queue.html'
    context_object_name = 'activities'

    def get_queryset(self):
        user = self.request.user
        couple = Couple.objects.filter(user1=user).first() or Couple.objects.filter(user2=user).first()
        if not couple:
            return Activity.objects.none()
        return couple.activities.filter(status='queued').order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context
    
class AcceptActivityView(LoginRequiredMixin, View):
    def post(self, request, pk):
        activity = get_object_or_404(Activity, pk=pk)
        if activity.added_by == request.user:
            messages.error(request, "You cannot accept your own activity.")
            return redirect('activity_list')
        activity.status = 'pool'
        activity.save()
        messages.success(request, "Activity accepted and added to pool.")
        return redirect('activity_list')

class RejectActivityView(LoginRequiredMixin, View):
    def post(self, request, pk):
        activity = get_object_or_404(Activity, pk=pk)
        if activity.added_by == request.user:
            messages.error(request, "You cannot reject your own activity.")
            return redirect('activity_list')
        activity.status = 'rejected'
        activity.save()
        messages.success(request, "Activity rejected and removed from queue.")
        return redirect('activity_list')
    
class ArchiveActivityView(LoginRequiredMixin, View):
    def post(self, request, pk):
        activity = get_object_or_404(Activity, pk=pk)
        couple = Couple.objects.filter(user1=request.user).first() or Couple.objects.filter(user2=request.user).first()
        if activity.couple != couple:
            messages.error(request, "Not authorized.")
            return redirect('home')

        activity.status = 'archived'
        activity.save()
        messages.success(request, "Activity archived. Great job!")
        return redirect('home')

class PostponeActivityView(LoginRequiredMixin, View):
    def post(self, request, pk):
        activity = get_object_or_404(Activity, pk=pk)
        couple = Couple.objects.filter(user1=request.user).first() or Couple.objects.filter(user2=request.user).first()
        if activity.couple != couple:
            messages.error(request, "Not authorized.")
            return redirect('home')

        activity.status = 'postponed'
        activity.last_suggested = None  # so it can be picked again next week
        activity.save()
        messages.success(request, "Activity postponed. We'll suggest another one next week.")
        return redirect('home')