from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from coursework.models import Key, User, Key_requests, Key_return_request, Key_transfer
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

# views.py
@login_required
def transfer_key(request, key_id):
    key = get_object_or_404(Key, id=key_id)

    if key.holder != request.user:
        messages.error(request, "Ви не володієте цим ключем.")
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('name')
        surname = request.POST.get('surname')

        try:
            new_holder = User.objects.get(name=name, surname=surname)
        except User.DoesNotExist:
            messages.error(request, 'Користувача не знайдено.')
            return redirect('transfer_key', key_id=key.id)

        existing_request = Key_transfer.objects.filter(
            from_user=request.user, key=key, is_approved=False,
            created_at__gte=timezone.now() - timedelta(minutes=15)
        ).first()
        if existing_request:
            messages.info(request, "Запит вже створено.")
        else:
            Key_transfer.objects.create(from_user=request.user, to_user=new_holder, key=key)
            messages.success(request, "Запит на передачу ключа створено.")

        return redirect('home')

    return render(request, 'transfer_page.html', {'key': key})



@login_required
def my_transfer_requests(request):
    requests = Key_transfer.objects.filter(
        to_user=request.user,
        is_approved=False,
        is_expired=False,
        created_at__gte=timezone.now() - timedelta(minutes=15)
    ).select_related('from_user', 'to_user', 'key')

    return render(request, 'transfer_request.html', {'requests': requests})

@login_required
def approve_transfer_request(request, request_id):
    if request.method == 'POST':
        transfer_request = get_object_or_404(Key_transfer, id=request_id)

        if transfer_request.is_valid():
            transfer_request.key.transfer_key(request.user)
            transfer_request.is_approved = True
            transfer_request.save()
            messages.success(request, "Ключ передано вам.")
        else:
            transfer_request.is_expired = True
            transfer_request.save()
            messages.error(request, "Запит недійсний або протермінований.")

        return redirect('home')

@staff_member_required
def reject_transfer_request(request, request_id):
    transfer_request = get_object_or_404(Key_transfer, id=request_id)

    if transfer_request.is_expired or transfer_request.is_approved:
        messages.error(request, "Цей запит уже оброблено.")
    else:
        transfer_request.is_expired = True
        transfer_request.save()

        key = transfer_request.key
        key.status = 'taken'
        key.save()

        messages.success(request, f"Запит на передачу ключа {key.auditory} відхилено.")

    return redirect('admin_transfer_requests')


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
        is_expired=False,
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

    existing_request = Key_return_request.objects.filter(
        user=request.user,
        key=key,
        is_expired=False,
        is_approved=False
    ).exists()

    if existing_request:
        messages.error(request, "Ви вже подали запит на повернення цього ключа.")
        return redirect('home')

    Key_return_request.objects.create(user=request.user, key=key)
    messages.success(request, "Запит на повернення ключа надіслано.")
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
    # expire_old_requests()
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

    return redirect('admin_put_request')

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

    if request.method == 'POST':
        return_request.is_expired = True
        return_request.save()

        messages.success(request, f"Запит на повернення ключа {return_request.key.auditory} відхилено.")

    return redirect('put_request')

@staff_member_required
def action_view(request):
    logs = []

    for req in Key_requests.objects.filter(is_approved=True, is_expired=False):
        logs.append({
            'timestamp': req.created_at,
            'text': f"{req.user.name} {req.user.surname} взяв ключ до {req.key.auditory}",
        })

    for ret in Key_return_request.objects.filter(is_approved=True, is_expired=False):
        logs.append({
            'timestamp': ret.created_at,
            'text': f"{ret.user.name} {ret.user.surname} поклав ключ від {ret.key.auditory}",
        })

    for tr in Key_transfer.objects.filter(is_approved=True, is_expired=False):
        logs.append({
            'timestamp': tr.created_at,
            'text': f"{tr.from_user.name} {tr.from_user.surname} передав ключ від {tr.key.auditory} користувачу " f"{tr.to_user.name} {tr.to_user.surname}"})

    logs.sort(key=lambda x: x['timestamp'], reverse=True)

    return render(request, 'action_view.html', {'logs': logs})