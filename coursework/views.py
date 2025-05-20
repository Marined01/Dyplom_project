from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from coursework.models import Key, User, Key_requests, Key_return_request
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect

def registration_page(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        email = request.POST.get('email')
        password = request.POST.get('password')

        data_error = False

        if User.objects.filter(email=email).exists():
            data_error = True
            messages.error(request, 'Така електронна адреса вже використовується')

        if len(password) < 8:
            data_error = True
            messages.error(request, 'Пароль має містити щонайменше 8 символів')

        if data_error:
            return redirect('registration')

        else:
            new_user = User.objects.create_user(name=name, surname=surname ,email=email, password=password)
            messages.success(request, 'Користувача створено')
            return redirect('login')

    return render(request, 'registration_page.html')

def login_page(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Неправильні дані для входу')
            return redirect('login')

    return render(request, 'login_page.html')

@login_required
def logout_page(request):
    logout(request)
    return redirect('login')

@login_required
def home_page(request):
    users_keys = Key.objects.filter(holder=request.user)
    return render(request, 'home_page.html', {'users_keys': users_keys})

@login_required
def key_list(request):
    keys = Key.objects.all()
    return render(request, 'key_list.html', {'keys': keys, 'user': request.user})

@login_required
def take_key(request, key_id):
    try:
        key = Key.objects.get(id=key_id)
    except Key.DoesNotExist:
        raise Http404("Key does not exist")
    try:
        key.take_key(request.user)
        messages.success(request, f"Ключ до аудиторії {key.auditory} взяли")
    except ValueError as e:
        messages.error(request, e)
    # referer = request.META.get('HTTP_REFERER')
    # return HttpResponseRedirect(referer)
    return redirect('home')

@login_required
def put_key(request, key_id):
    try:
        key = Key.objects.get(id=key_id)
    except Key.DoesNotExist:
        raise Http404("Key does not exist")
    try:
        key.put_key()
        messages.success(request, f"Ключ до аудиторії {key.auditory} поклали")
    except ValueError as e:
        messages.error(request, e)
    return redirect('home')


@login_required
def transfer_key(request, key_id):
    try:
        key = Key.objects.get(id=key_id)
    except Key.DoesNotExist:
        messages.error(request, 'Ключ не знайдено.')
        return redirect('transfer_key')

    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        try:
            new_holder = User.objects.get(name=name, surname=surname)
        except User.DoesNotExist:
            messages.error(request, 'Неправильні дані користувача, або не існує')
            redirect('transfer_key')

        try:
            key.transfer_key(new_holder)
            messages.success(request, 'Ключ передано користувачу {user.name} {user.surname}')
            return redirect('home')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('transfer_key')

    return render(request, 'transfer_page.html')

@login_required
def free_keys(request):
    free_keys = Key.objects.filter(
        status='free'
    )
    # .exclude(
    #     key_requests__is_approved=False,
    #     key_requests__is_expired=False,
    #     key_requests__created_at__gte=timezone.now() - timedelta(minutes=15)
    # )
    return render(request, 'free_keys_page.html', {'free_keys': free_keys})

@login_required
def profile(request):
    return render(request, 'profile_page.html', {'user': request.user}  )

@login_required
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        # user.name = request.POST['name']
        # user.surname = request.POST['surname']
        user.email = request.POST['email']
        password = request.POST.get('password')
        if password:
            user.set_password(password)
        user.save()
        messages.success(request, 'Профіль оновлено успішно.')
        return redirect('home')
    return render(request, 'edit_profile_page.html')


@login_required
def take_key_request(request, key_id):
    key = get_object_or_404(Key, id=key_id)
    existing_request = Key_requests.objects.filter(
        key=key,
        is_approved=False,
        created_at__gte=timezone.now() - timedelta(minutes=15)
    ).first()

    if existing_request:
        messages.error(request, "Ключ вже має активний запит.")
        return redirect('home')

    active_keys = Key.objects.filter(holder=request.user, status='taken').count()
    if active_keys >= 4:
        messages.error(request, "Ви не можете мати більше 4 ключів одночасно.")
        return redirect('home')

    Key_requests.objects.create(user=request.user, key=key)
    key.status = 'pending'
    key.save()

    messages.success(request, f"Запит на ключ {key.auditory} надіслано адміністратору.")
    return redirect('home')


@login_required
def put_key_request(request, key_id):
    key = get_object_or_404(Key, id=key_id)
    if key.holder != request.user:
        messages.error(request, "Ви не володієте цим ключем.")
        return redirect('home')

    existing_request = Key_return_request.objects.filter(
        key=key,
        is_approved=False,
        created_at__gte=timezone.now() - timedelta(minutes=15)
    ).first()
    if existing_request:
        messages.info(request, "Запит на повернення вже створено.")
    else:
        Key_return_request.objects.create(user=request.user, key=key)
        messages.success(request, "Запит на повернення ключа надіслано адміністратору.")
    return redirect('home')

def expire_old_requests():
    fifteen_minutes_ago = timezone.now() - timedelta(minutes=15)

    Key_requests.objects.filter(
        is_approved=False,
        is_expired=False,
        created_at__lt=fifteen_minutes_ago
    ).update(is_expired=True)

    Key_return_request.objects.filter(
        is_approved=False,
        is_expired=False,
        created_at__lt=fifteen_minutes_ago
    ).update(is_expired=True)

@staff_member_required
def admin_key_request(request):
    expire_old_requests()
    active_take_request = Key_requests.objects.filter(is_approved=False,
                                                      is_expired=False,
                                                      created_at__gte=timezone.now() - timedelta(minutes=15)).select_related('key', 'user')
    return render(request, 'admin_key_requests.html', {'requests': active_take_request})

@staff_member_required
def admin_put_request(request):
    expire_old_requests()
    active_put_request = Key_return_request.objects.filter(is_approved=False,
                                                           is_expired=False,
                                                           created_at__gte=timezone.now() - timedelta(minutes=15)).select_related('key', 'user')
    return render(request, 'admin_put_requests.html', {'requests': active_put_request})

@staff_member_required
def approve_key_request(request, request_id):
    if request.method == 'POST':
        key_request = get_object_or_404(Key_requests, id=request_id)

        if key_request.is_valid():
            key = key_request.key
            try:
                key.take_key(key_request.user)
                key_request.is_approved = True
                key_request.save()
                messages.success(request, f"Ключ до {key.auditory} підтверджено.")
            except ValueError as e:
                messages.error(request, str(e))
        else:
            messages.error(request, "Запит недійсний або вже оброблений.")

    return redirect('key_request')

@staff_member_required
def approve_return_request(request, request_id):
    if request.method == 'POST':
        return_request = get_object_or_404(Key_return_request, id=request_id)
        if return_request.is_valid():
            return_request.key.put_key()

            return_request.is_approved = True
            return_request.save()
            messages.success(request, f"Ключ {return_request.key.auditory} успішно повернено.")

        else:
            return_request.is_expired = True
            return_request.save()
            messages.error(request, "Час дії запиту минув або вже оброблений.")

    return redirect('admin_key_request')

@staff_member_required
def reject_key_request(request, request_id):
    if request.method == 'POST':
        key_request = get_object_or_404(Key_requests, id=request_id)
        key_request.is_expired = True
        key_request.save()

        key = key_request.key
        key.status = 'free'
        key.holder = None
        key.save()

        messages.info(request, f"Запит на ключ {key.auditory} відхилено.")
    return redirect('home')

@staff_member_required
def reject_return_request(request, request_id):
    return_request = get_object_or_404(Key_return_request, id=request_id)
    return_request.is_expired = True
    return_request.save()
    messages.info(request, "Запит на повернення ключа скасовано.")
    return redirect('return_requests_list')

# @staff_member_required
# def admin_key_request(request):
#     take_requests = Key_requests.objects.filter(is_approved=False, is_expired=False)
#     return_requests = Key_return_request.objects.filter(is_approved=False, is_expired=False)
#
#     return render(request, 'admin_key_requests.html', {
#         'take_requests': take_requests,
#         'return_requests': return_requests
#     })
