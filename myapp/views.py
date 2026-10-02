from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.hashers import check_password,make_password
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.views.decorators.http import require_POST
from .models import User
from .permissions import permission_required

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        phone_number = request.POST.get('phone_number','').strip()
        password = request.POST.get('password','')
        passwrd2 = request.POST.get('password2','')
        context = {'username':username,'phone_number':phone_number}
        
        if not username or not password or not phone_number or not passwrd2:
            context['error'] = 'Ҳамаи майдонҳоро пур кунед'
            return render(request,'register.html',context)
        if password != passwrd2:
            context['error'] = 'Рамзҳо бояд якхела бошанд'
            return render(request,'register.html',context)
        if User.objects.filter(username=username).exists():
            context['error'] = 'Ин номи корбар аллакай вуҷуд дорад'
            return render(request,'register.html',context)
        if User.objects.filter(phone_number=phone_number).exists():
            context['error'] = 'Ин рақами телефон аллакай вуҷуд дорад'
            return render(request,'register.html',context)
        User.objects.create(username=username,phone_number=phone_number,password=make_password(password))
        return redirect('login')
    
    return render(request,'register.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username','').strip()
        phone_number = request.POST.get('phone_number','').strip()
        password = request.POST.get('password','')
        context = {'username':username,'phone_number':phone_number}
        
        user = None

        for item in User.objects.filter(username=username,phone_number=phone_number):
            if check_password(password,item.password):
                user = item
                break
            if password == item.password:
                item.password = make_password(password)
                item.save(update_fields=['password'])
                user = item
                break

        if user is None:
            context['error'] = 'Номи корбар ё рамз нодуруст аст'
            return render(request,'login.html',context)
        
        request.session['user_id'] = user.id
        return redirect('dahsboard')
    return  render(request,'login.html')
        
        
def logauttt(request):
    request.session.flush()
    return redirect('register')


from django.urls import reverse_lazy
from django.views.generic import CreateView,ListView,UpdateView,DeleteView,DetailView

from . models import *
from .forms import BuildingForm ,ApartmentFrom ,InquiryFrom,BookingForm,SaleForm



def update_apartment_status(apartment):
    if Sale.objects.filter(apartment=apartment).exists():
        status = 'sold'
    elif Booking.objects.filter(apartment=apartment,status='confirmed').exists():
        status = 'booked'
    else:
        status = 'available'

    if apartment.status != status:
        apartment.status = status
        apartment.save(update_fields=['status'])

class LoginMixin:
    def dispatch(self,request,*args,**kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return super().dispatch(request,*args,**kwargs)
    

class Bulindingcreat(LoginMixin,CreateView):
    model = Building
    form_class = BuildingForm
    template_name = 'bulding_c.html'
    success_url = reverse_lazy('bulding_all')
    
    
class BUlding_all(LoginMixin,ListView):
    model = Building
    template_name = 'bulding_all.html'
    context_object_name = 'buldings' 
    
class bolding_up(LoginMixin,UpdateView):
    model = Building
    form_class = BuildingForm
    template_name = 'bulding_up.html'
    success_url = reverse_lazy('bulding_all')
    

class boldingDetail(LoginMixin,DetailView):
    model = Building
    template_name = 'bolding_detail.html'
    context_object_name = 'detail'

    def get_queryset(self):
        return Building.objects.prefetch_related('apartments')
    
class bulding_delete(LoginMixin,DeleteView):
    model = Building
    template_name = 'delte_b.html'
    success_url = reverse_lazy('bulding_all')

    def form_valid(self,form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            context = self.get_context_data(
                error='Аввал квартираҳои вобаста ба ин биноро нест кунед'
            )
            return self.render_to_response(context)
        
       

class ApartmentDetail(LoginMixin,DetailView):
    model = Apartment
    template_name = 'apartment_detail.html'
    context_object_name = 'apartment'

    def get_queryset(self):
        return Apartment.objects.select_related('building')
    
class Apartment_cr(LoginMixin,CreateView):
    model = Apartment
    form_class = ApartmentFrom
    template_name = 'apartment_cr.html'
    success_url = reverse_lazy('apartment_all')
    
    
class apartment_all(LoginMixin,ListView):
    model = Apartment
    template_name = 'apartment_all.html'
    context_object_name = 'buldings' 
    
class Apartment_up(LoginMixin,UpdateView):
    model = Apartment
    form_class = ApartmentFrom
    template_name = 'apartment_up.html'
    success_url = reverse_lazy('apartment_all')
    

    
class apartment_delete(LoginMixin,DeleteView):
    model = Apartment
    template_name = 'delte_a.html'
    success_url = reverse_lazy('apartment_all')

    def form_valid(self,form):
        try:
            return super().form_valid(form)
        except ProtectedError:
            context = self.get_context_data(
                error='Ин квартира дар дархост, брон ё фурӯш истифода шудааст ва нест намешавад'
            )
            return self.render_to_response(context)
    

class Inquiry_creat(LoginMixin,CreateView):
    model = Inquiry
    form_class = InquiryFrom
    template_name = 'inquiry_c.html'
    success_url = reverse_lazy('inquiry_all')
    
    
class Inquiry_all(LoginMixin,ListView):
    model = Inquiry
    template_name = 'inquiry_all.html'
    context_object_name = 'inquiries' 
    
class MyInquiries(LoginMixin, ListView):
    model = Inquiry
    template_name = "my_inquiries.html"
    context_object_name = "inquiries"

    def get_queryset(self):
        user_id = self.request.session["user_id"]
        return Inquiry.objects.filter(user_id=user_id)
    
        
class Inquiry_up(LoginMixin,UpdateView):
    model = Inquiry
    form_class = InquiryFrom
    template_name = 'inquiry_up.html'
    success_url = reverse_lazy('inquiry_all')
    
    
class Inquiry_delete(LoginMixin,DeleteView):
    model = Inquiry
    template_name = 'delte_i.html'
    success_url = reverse_lazy('inquiry_all')

class Booking_creat(LoginMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'booking_cr.html'
    success_url = reverse_lazy('booking_all')

    def form_valid(self,form):
        response = super().form_valid(form)
        update_apartment_status(self.object.apartment)
        return response


class Booking_all(LoginMixin, ListView):
    model = Booking
    template_name = 'booking_all.html'
    context_object_name = 'bookings'
    
class MyBookings(LoginMixin, ListView):
    model = Booking
    template_name = "my_bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        user_id = self.request.session["user_id"]
        return Booking.objects.filter(user_id=user_id)

class Booking_up(LoginMixin, UpdateView):
    model = Booking
    form_class = BookingForm
    template_name = 'booking_up.html'
    success_url = reverse_lazy('booking_all')

    def form_valid(self,form):
        old_apartment = self.get_object().apartment
        response = super().form_valid(form)
        update_apartment_status(old_apartment)
        update_apartment_status(self.object.apartment)
        return response

class Booking_delete(LoginMixin, DeleteView):
    model = Booking
    template_name = 'delte_booking.html'
    success_url = reverse_lazy('booking_all')

    def form_valid(self,form):
        apartment = self.object.apartment
        response = super().form_valid(form)
        update_apartment_status(apartment)
        return response


@require_POST
def booking_confirm(request,pk):
    if not request.session.get('user_id'):
        return redirect('login')

    booking = get_object_or_404(Booking,pk=pk)

    if booking.apartment.status == 'sold':
        return redirect('booking_all')

    Booking.objects.filter(
        apartment=booking.apartment,
        status__in=['pending','confirmed'],
    ).exclude(pk=booking.pk).update(status='rejected')

    booking.status = 'confirmed'
    booking.save(update_fields=['status'])
    update_apartment_status(booking.apartment)
    return redirect('booking_all')


@require_POST
def booking_reject(request,pk):
    if not request.session.get('user_id'):
        return redirect('login')

    booking = get_object_or_404(Booking,pk=pk)
    booking.status = 'rejected'
    booking.save(update_fields=['status'])
    update_apartment_status(booking.apartment)
    return redirect('booking_all')


@require_POST
def booking_cancel(request,pk):
    if not request.session.get('user_id'):
        return redirect('login')

    booking = get_object_or_404(Booking,pk=pk)
    booking.status = 'cancelled'
    booking.save(update_fields=['status'])
    update_apartment_status(booking.apartment)
    return redirect('booking_all')

    
    
class Sale_creat(LoginMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = 'sale_cr.html'
    success_url = reverse_lazy('sale_all')

    @transaction.atomic
    def form_valid(self, form):
        apartment = form.cleaned_data['apartment']

        if apartment.status == 'sold' or Sale.objects.filter(apartment=apartment).exists():
            form.add_error(
                'apartment',
                'Ин квартира аллакай фурӯхта шудааст'
            )
            return self.form_invalid(form)

        response = super().form_valid(form)

        Booking.objects.filter(
            apartment=apartment,
            status__in=['pending','confirmed'],
        ).update(status='cancelled')

        apartment.status = 'sold'
        apartment.save(update_fields=['status'])

        return response
    
class Sale_all(LoginMixin, ListView):
    model = Sale
    template_name = 'sale_all.html'
    context_object_name = 'sales'
    
class Sale_detail(LoginMixin, DetailView):
    model = Sale
    template_name = 'sale_detail.html'
    context_object_name = 'sale'
    
    
from decimal import Decimal, InvalidOperation
import os

from django.db.models import Q
from django.http import JsonResponse
from groq import APIError, Groq



# poiskkkk
def apartment_search(request):
    query = request.GET.get("q", "").strip()[:100]
    building = request.GET.get("building", "").strip()[:100]
    floor = request.GET.get("floor", "").strip()
    rooms = request.GET.get("rooms", "").strip()
    max_price = request.GET.get("max_price", "").strip()[:32]

    apartments = Apartment.objects.select_related("building")
    if request.app_user.role == "user":
        apartments = apartments.filter(
            is_active=True, building__is_active=True, status="available"
        )

    if query:
        match = Q(building__name__icontains=query) | Q(building__address__icontains=query)
        if query.isdigit() and len(query) <= 18:
            match |= Q(number=int(query))
        apartments = apartments.filter(match)
    if building:
        apartments = apartments.filter(building__name__icontains=building)
    if floor.isdigit():
        apartments = apartments.filter(floor=int(floor))
    if rooms.isdigit():
        apartments = apartments.filter(rooms=int(rooms))
    if max_price:
        try:
            price_limit = Decimal(max_price)
            if price_limit.is_finite() and price_limit >= 0:
                apartments = apartments.filter(price__lte=price_limit)
        except InvalidOperation:
            pass

    return render(request, "apartment_search.html", {
        "apartments": apartments.order_by("building__name", "number"),
        "q": query,
        "building": building,
        "floor": floor,
        "rooms": rooms,
        "max_price": max_price,
    })

# aii  
def ai_chat(request):
    history = request.session.get("ai_chat_history", [])
    context = {"history": history}
    wants_json = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "GET" and wants_json:
        return JsonResponse({"history": history})

    if request.method == "POST":
        question = request.POST.get("question", "").strip()[:1500]
        context["question"] = question
        api_key = os.getenv("GROQ_API_KEY")

        if not question:
            context["error"] = "Напишите сообщение."
        elif not api_key:
            context["error"] = "AI-чат пока не настроен: нужен GROQ_API_KEY."
        else:
            try:
                client = Groq(api_key=api_key, timeout=30.0, max_retries=0)
                messages = [{
                    "role": "system",
                    "content": "Ты помощник сервиса Manzil по зданиям и квартирам. Отвечай кратко на языке пользователя. Не выдумывай наличие квартир, цены или статусы: если нет данных, предложи открыть поиск квартир.",
                }]
                messages.extend(history[-8:])
                messages.append({"role": "user", "content": question})
                response = client.chat.completions.create(
                    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
                    messages=messages,
                    max_completion_tokens=700,
                    reasoning_effort="low",
                )
                answer = (response.choices[0].message.content or "").strip()
                if not answer:
                    context["error"] = "AI не вернул ответ. Попробуйте ещё раз."
                else:
                    history = (history + [
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": answer},
                    ])[-10:]
                    request.session["ai_chat_history"] = history
                    context.update(answer=answer, history=history)
            except APIError as exc:
                if getattr(exc, "status_code", None) in (401, 403):
                    context["error"] = "Калиди AI нодуруст аст ё иҷозати истифода надорад."
                elif getattr(exc, "status_code", None) == 429:
                    context["error"] = "Маҳдудияти дархостҳои AI расид. Каме баъд кӯшиш кунед."
                else:
                    context["error"] = "AI ҳоло ҷавоб дода натавонист. Каме баъд кӯшиш кунед."

        if wants_json:
            status = 200 if context.get("answer") else 400
            return JsonResponse({
                "answer": context.get("answer", ""),
                "error": context.get("error", ""),
            }, status=status)

    return render(request, "ai_chat.html", context)
