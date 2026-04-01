import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import razorpay

from .forms import RegistrationForm, ContactForm
from .models import (
    Event,
    Registration,
    SportsVenue,
    Coaching,
    Society,
    Payment,
    Contact,
)

logger = logging.getLogger(__name__)

# Razorpay client setup
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


# View for displaying all events
def event_list(request):
    events = Event.objects.all()

    # 🔹 Find events this user has already registered for (completed payments only)
    registered_event_ids = []
    if request.user.is_authenticated:
        registered_event_ids = list(
            Registration.objects.filter(
                user=request.user,
                payment_status="Completed",
            ).values_list("event_id", flat=True)
        )

    return render(
        request,
        "registration/event_list.html",
        {
            "events": events,
            "registered_event_ids": registered_event_ids,
        },
    )


@login_required
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        # Redirect to the payment page when the button is clicked
        return HttpResponseRedirect(reverse("process_payment", args=[event_id]))

    return render(request, "registration/register_event.html", {"event": event})


def home(request):
    # Fetch upcoming events to show in the carousel
    events = Event.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile_number = request.POST.get("mobile")
        message = request.POST.get("message")

        # Save the contact details to the database
        contact = Contact(
            name=name,
            email=email,
            mobile_number=mobile_number,
            message=message,
        )
        contact.save()

        messages.success(request, "Your message has been sent successfully.")
        return redirect("home")

    return render(request, "registration/home.html", {"events": events})


# View for displaying all sports venues
def sports_venues(request):
    venues = SportsVenue.objects.all()
    return render(request, "registration/sports_venues.html", {"venues": venues})


# View for displaying all coaching sessions
def coaching(request):
    coachings = Coaching.objects.all()
    return render(request, "registration/coaching.html", {"coachings": coachings})


# Register View
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


# Login View
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")

                # Admin vs normal user redirect
                if user.is_staff or user.is_superuser:
                    return redirect("/admin/")
                else:
                    return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


# Logout View
def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect("home")


# View to display all societies and their available coaches and sports
def society_list(request):
    societies = Society.objects.all()
    return render(request, "registration/society_list.html", {"societies": societies})


@login_required
def process_payment(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user = request.user

    # 🔹 1. Check if this user already has a COMPLETED registration for this event
    existing_registration = Registration.objects.filter(
        user=user,
        event=event,
        payment_status="Completed",
    ).first()

    if existing_registration:
        messages.info(request, "You have already registered for this event.")
        # You can change this to an event detail view if you have one
        return redirect("event_list")

    # 🔹 2. If no completed registration, move to payment flow
    if request.method == "POST":
        amount = int(event.registration_fee * 100)  # Convert registration fee to paise

        # Create Razorpay order
        order_data = {
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1",
        }

        try:
            order = razorpay_client.order.create(data=order_data)
        except Exception as e:
            logger.exception("Error creating Razorpay order")
            messages.error(
                request,
                "There was a problem initiating the payment. Please try again.",
            )
            return redirect("event_list")

        # 👉 Only create Payment here, NOT Registration yet
        payment = Payment.objects.create(
            order_id=order["id"],
            amount=amount / 100,  # rupees
            status="Pending",
            event=event,
            user=user,
        )

        return render(
            request,
            "registration/payment.html",
            {
                "order_id": order["id"],
                "event": event,
                "amount": amount,
                "razorpay_key": settings.RAZORPAY_KEY_ID,
            },
        )

    return HttpResponse("Invalid request method.", status=405)


@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        if not razorpay_order_id:
            return HttpResponse("Missing order id.", status=400)

        try:
            payment = Payment.objects.get(order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return HttpResponse("Payment record not found.", status=404)

        # Optional: Verify payment signature
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
        except razorpay.errors.SignatureVerificationError:
            payment.status = "Failed"
            payment.save()
            return HttpResponse("Payment verification failed.", status=400)

        # Mark the payment as completed
        payment.status = "Completed"
        payment.save()

        # 🔹 Create or update Registration ONLY AFTER successful payment
        registration, created = Registration.objects.get_or_create(
            user=payment.user,
            event=payment.event,
            defaults={"payment_status": "Completed"},
        )

        if not created:
            registration.payment_status = "Completed"
            registration.save()

        return render(
            request,
            "registration/payment_success.html",
            {"event": payment.event},
        )

    return HttpResponse("Invalid request method.", status=405)


def about(request):
    company_info = {
        "name": "Sportify",
        "description": """
            Sportify is a dynamic platform designed to bring sports enthusiasts together. We specialize in organizing
            sports events, providing coaching sessions, and offering top-tier sports venues for both casual players and
            professionals. Whether you're looking to participate in an upcoming tournament, find a venue for a friendly 
            match, or enroll in a coaching session to hone your skills, Sportify has got you covered.
        """,
        "mission": "Our mission is to promote active and healthy lifestyles through sports and community engagement.",
        "vision": "To become the world’s leading sports platform where athletes, coaches, and venues are seamlessly connected.",
        "team": [
            {
                "name": "Omkar",
                "position": "CEO",
                "bio": "Omkar is passionate about sports and has over 10 years of experience in sports event management.",
            },
            {
                "name": "Atul",
                "position": "Head Coach",
                "bio": "Atul is a former professional athlete and now leads our coaching division.",
            },
            {
                "name": "Sameer",
                "position": "Operations Manager",
                "bio": "Sameer ensures everything runs smoothly, from venue management to event organization.",
            },
        ],
    }
    return render(request, "registration/about.html", {"company_info": company_info})


def contact(request):
    company_info = {
        "name": "Sportify",
        "email": "omkary357@gmail.com",
        "phone": "+91 7715078272",
        "address": "MIDC, Andheri East, Mumbai, Maharashtra 400093, India",
        "website": "www.sportify.com",
    }
    return render(request, "registration/contact.html", {"company_info": company_info})
