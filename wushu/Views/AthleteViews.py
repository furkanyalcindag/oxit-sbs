from datetime import timedelta, datetime

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect

from wushu.Forms.BeltForm import BeltForm
from wushu.Forms.CategoryItemForm import CategoryItemForm
from wushu.Forms.CommunicationForm import CommunicationForm
from wushu.Forms.DisabledCommunicationForm import DisabledCommunicationForm
from wushu.Forms.DisabledPersonForm import DisabledPersonForm
from wushu.Forms.DisabledUserForm import DisabledUserForm
from wushu.Forms.LicenseForm import LicenseForm
from wushu.Forms.UserForm import UserForm
from wushu.Forms.PersonForm import PersonForm
from wushu.Forms.UserSearchForm import UserSearchForm
from wushu.models import Athlete, CategoryItem, Person, Communication, License, SportClubUser, SportsClub
from wushu.models.EnumFields import EnumFields
from wushu.models.Level import Level
from wushu.services import general_methods


@login_required
def return_add_athlete(request):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    user_form = UserForm()
    person_form = PersonForm()
    communication_form = CommunicationForm()

    if request.method == 'POST':

        user_form = UserForm(request.POST)
        person_form = PersonForm(request.POST, request.FILES)
        communication_form = CommunicationForm(request.POST)

        if user_form.is_valid() and person_form.is_valid() and communication_form.is_valid():
            user = User()
            user.username = user_form.cleaned_data['email']
            user.first_name = user_form.cleaned_data['first_name']
            user.last_name = user_form.cleaned_data['last_name']
            user.email = user_form.cleaned_data['email']
            group = Group.objects.get(name='Sporcu')
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            user.groups.add(group)
            user.save()

            person = person_form.save(commit=False)
            communication = communication_form.save(commit=False)
            person.save()
            communication.save()

            athlete = Athlete(
                user=user, person=person, communication=communication,
            )

            athlete.save()

            # subject, from_email, to = 'WUSHU - Sporcu Bilgi Sistemi Kullanıcı Giriş Bilgileri', 'ik@oxityazilim.com', user.email
            # text_content = 'Aşağıda ki bilgileri kullanarak sisteme giriş yapabilirsiniz.'
            # html_content = '<p> <strong>Site adresi: </strong> <a href="https://www.twf.gov.tr/"></a>https://www.twf.gov.tr/</p>'
            # html_content = html_content + '<p><strong>Kullanıcı Adı:  </strong>' + user.username + '</p>'
            # html_content = html_content + '<p><strong>Şifre: </strong>' + password + '</p>'
            # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()

            messages.success(request, 'Sporcu Başarıyla Kayıt Edilmiştir.')

            return redirect('wushu:update-athletes', pk=athlete.pk)

        else:
            for x in user_form.errors.as_data():
                messages.warning(request, user_form.errors[x][0])


    return render(request, 'sporcu/sporcu-ekle.html',
                  {'user_form': user_form, 'person_form': person_form, 'communication_form': communication_form

                   })


@login_required
def return_athletes(request):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    login_user = request.user
    user = User.objects.get(pk=login_user.pk)
    if user.groups.filter(name='KulupUye'):
        sc_user = SportClubUser.objects.get(user=user)
        clubsPk = []
        clubs = SportsClub.objects.filter(clubUser=sc_user)
        for club in clubs:
            clubsPk.append(club.pk)
        athletes = Athlete.objects.filter(licenses__sportsClub__in=clubsPk).distinct()
    elif user.groups.filter(name__in=['Yonetim', 'Admin']):
        athletes = Athlete.objects.all()
    user_form = UserSearchForm()

    if request.method == 'POST':
        user_form = UserSearchForm(request.POST)
        if user_form.is_valid():
            firstName = user_form.cleaned_data.get('first_name')
            lastName = user_form.cleaned_data.get('last_name')
            email = user_form.cleaned_data.get('email')
            if not (firstName or lastName or email):
                messages.warning(request, 'Lütfen Arama Kriteri Giriniz.')
            else:
                query = Q()
                if lastName:
                    query &= Q(user__last_name__icontains=lastName)
                if firstName:
                    query &= Q(user__first_name__icontains=firstName)
                if email:
                    query &= Q(user__email__icontains=email)
                athletes = Athlete.objects.filter(query)

    return render(request, 'sporcu/sporcular.html', {'athletes': athletes, 'user_form': user_form})


@login_required
def updateathletes(request, pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    athlete = Athlete.objects.get(pk=pk)
    belts_form = athlete.belts.all()
    licenses_form = athlete.licenses.all()
    user = User.objects.get(pk=athlete.user.pk)
    person = Person.objects.get(pk=athlete.person.pk)
    communication = Communication.objects.get(pk=athlete.communication.pk)

    user_form = UserForm(request.POST or None, instance=user)
    person_form = PersonForm(request.POST or None, instance=person)
    communication_form = CommunicationForm(request.POST or None, instance=communication)

    if request.method == 'POST':

        if user_form.is_valid() and communication_form.is_valid() and person_form.is_valid():
            user = user_form.save(commit=False)
            user.username = user_form.cleaned_data['email']
            user.first_name = user_form.cleaned_data['first_name']
            user.last_name = user_form.cleaned_data['last_name']
            user.email = user_form.cleaned_data['email']
            user.save()
            person_form.save()
            communication_form.save()

            messages.success(request, 'Sporcu Başarıyla Güncellenmiştir.')
            return redirect('wushu:update-athletes', pk=pk)

        else:

            messages.warning(request, 'Alanları Kontrol Ediniz')

    return render(request, 'sporcu/sporcuDuzenle.html',
                  {'user_form': user_form, 'communication_form': communication_form,
                   'person_form': person_form, 'belts_form': belts_form, 'licenses_form': licenses_form,
                   'athlete': athlete})


@login_required
def return_belt(request):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    category_item_form = CategoryItemForm();

    if request.method == 'POST':

        category_item_form = CategoryItemForm(request.POST)

        if category_item_form.is_valid():

            categoryItem = category_item_form.save(commit=False)
            categoryItem.forWhichClazz = "BELT"
            categoryItem.save()
            messages.success(request, 'Kuşak Başarıyla Kayıt Edilmiştir.')
            return redirect('wushu:kusak')

        else:

            messages.warning(request, 'Alanları Kontrol Ediniz')
    categoryitem = CategoryItem.objects.filter(forWhichClazz="BELT")
    return render(request, 'sporcu/kusak.html',
                  {'category_item_form': category_item_form, 'categoryitem': categoryitem})


@login_required
def categoryItemDelete(request, pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    if request.method == 'POST' and request.is_ajax():
        try:
            obj = CategoryItem.objects.get(pk=pk)
            obj.delete()
            return JsonResponse({'status': 'Success', 'messages': 'save successfully'})
        except CategoryItem.DoesNotExist:
            return JsonResponse({'status': 'Fail', 'msg': 'Object does not exist'})

    else:
        return JsonResponse({'status': 'Fail', 'msg': 'Not a valid request'})


@login_required
def categoryItemUpdate(request, pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    categoryItem = CategoryItem.objects.get(id=pk)
    category_item_form = CategoryItemForm(request.POST or None, instance=categoryItem,
                                          initial={'parent': categoryItem.parent})
    if request.method == 'POST':
        if category_item_form.is_valid():
            category_item_form.save()
            messages.success(request, 'Başarıyla Güncellendi')
            return redirect('wushu:kusak')
        else:
            messages.warning(request, 'Alanları Kontrol Ediniz')

    return render(request, 'sporcu/kusakDuzenle.html',
                  {'category_item_form': category_item_form})


@login_required
def sporcu_kusak_ekle(request, pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    athlete = Athlete.objects.get(pk=pk)
    belt_form = BeltForm(request.POST, request.FILES or None)
    belt_form.fields['definition'].queryset = CategoryItem.objects.filter(forWhichClazz='BELT',
                                                                          branch=athlete.licenses.last().branch)

    if request.method == 'POST':
        belt_form = BeltForm(request.POST, request.FILES or None)
        if belt_form.is_valid():
            belt = Level(startDate=belt_form.cleaned_data['startDate'],
                         dekont=belt_form.cleaned_data['dekont'],
                         definition=belt_form.cleaned_data['definition'])
            belt.levelType = EnumFields.LEVELTYPE.BELT
            belt.branch = athlete.licenses.last().branch
            belt.status = Level.WAITED
            belt.save()
            athlete.belts.add(belt)
            athlete.save()

            messages.success(request, 'Kuşak Başarıyla Eklenmiştir.')
            return redirect('wushu:update-athletes', pk=pk)

        else:

            messages.warning(request, 'Alanları Kontrol Ediniz')

    return render(request, 'sporcu/sporcu-kusak-ekle.html',
                  {'belt_form': belt_form})


@login_required
def sporcu_kusak_duzenle(request, belt_pk, athlete_pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    belt = Level.objects.get(pk=belt_pk)
    belt_form = BeltForm(request.POST, request.FILES or None, instance=belt, initial={'definition': belt.definition})
    if request.method == 'POST':
        if belt_form.is_valid():
            belt_form.save()

            messages.success(request, 'Kuşak Onaya Gönderilmiştir.')
            return redirect('wushu:update-athletes', pk=athlete_pk)

        else:

            messages.warning(request, 'Alanları Kontrol Ediniz')

    return render(request, 'sporcu/sporcu-kusak-duzenle.html',
                  {'belt_form': belt_form})


@login_required
def sporcu_kusak_sil(request, pk, athlete_pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    if request.method == 'POST' and request.is_ajax():
        try:
            obj = Level.objects.get(pk=pk)
            athlete = Athlete.objects.get(pk=athlete_pk)
            athlete.belts.remove(obj)
            obj.delete()
            return JsonResponse({'status': 'Success', 'messages': 'save successfully'})
        except Level.DoesNotExist:
            return JsonResponse({'status': 'Fail', 'msg': 'Object does not exist'})

    else:
        return JsonResponse({'status': 'Fail', 'msg': 'Not a valid request'})


@login_required
def sporcu_lisans_ekle(request, pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    athlete = Athlete.objects.get(pk=pk)
    user = request.user

    license_form = LicenseForm(request.POST, request.FILES or None)

    if user.groups.filter(name='KulupUye'):
        sc_user = SportClubUser.objects.get(user=user)
        clubs = SportsClub.objects.filter(clubUser=sc_user)
        clubsPk = []
        for club in clubs:
            clubsPk.append(club.pk)
        license_form.fields['sportsClub'].queryset = SportsClub.objects.filter(id__in=clubsPk)

    elif user.groups.filter(name__in=['Yonetim', 'Admin']):
        license_form.fields['sportsClub'].queryset = SportsClub.objects.all()

    if request.method == 'POST':
        license_form = LicenseForm(request.POST, request.FILES or None)
        if license_form.is_valid():
            license = license_form.save()
            athlete.licenses.add(license)

            messages.success(request, 'Lisans Başarıyla Eklenmiştir.')
            return redirect('wushu:update-athletes', pk=pk)

        else:

            messages.warning(request, 'Alanları Kontrol Ediniz')

    return render(request, 'sporcu/sporcu-lisans-ekle.html',
                  {'license_form': license_form})


@login_required
def sporcu_lisans_onayla(request, license_pk, athlete_pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    license = License.objects.get(pk=license_pk)
    license.status = License.APPROVED
    license.save()

    messages.success(request, 'Lisans Onaylanmıştır')
    return redirect('wushu:update-athletes', pk=athlete_pk)


@login_required
def sporcu_lisans_reddet(request, license_pk, athlete_pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    license = License.objects.get(pk=license_pk)
    license.status = License.DENIED
    license.save()

    messages.success(request, 'Lisans Reddedilmiştir')
    return redirect('wushu:update-athletes', pk=athlete_pk)


@login_required
def sporcu_lisans_listesi_onayla(request, license_pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    license = License.objects.get(pk=license_pk)
    license.status = License.APPROVED
    license.save()
    messages.success(request, 'Lisans Onaylanmıştır')
    return redirect('wushu:lisans-listesi')


@login_required
def sporcu_kusak_listesi_onayla(request, belt_pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    belt = Level.objects.get(pk=belt_pk)
    belt.status = Level.APPROVED
    belt.save()
    messages.success(request, 'Kuşak Onaylanmıştır')
    return redirect('wushu:kusak-listesi')


@login_required
def sporcu_kusak_onayla(request, belt_pk, athlete_pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    belt = Level.objects.get(pk=belt_pk)
    belt.status = Level.APPROVED
    belt.save()

    messages.success(request, 'Kuşak Onaylanmıştır')
    return redirect('wushu:update-athletes', pk=athlete_pk)


@login_required
def sporcu_kusak_reddet(request, belt_pk, athlete_pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    belt = Level.objects.get(pk=belt_pk)
    belt.status = Level.DENIED
    belt.save()

    messages.success(request, 'Kuşak Reddedilmiştir')
    return redirect('wushu:update-athletes', pk=athlete_pk)


@login_required
def sporcu_lisans_duzenle(request, license_pk, athlete_pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    license = License.objects.get(pk=license_pk)
    license_form = LicenseForm(request.POST or None, request.FILES or None, instance=license,
                               initial={'sportsClub': license.sportsClub})
    user = request.user
    if user.groups.filter(name='KulupUye'):
        sc_user = SportClubUser.objects.get(user=user)
        clubs = SportsClub.objects.filter(clubUser=sc_user)
        clubsPk = []
        for club in clubs:
            clubsPk.append(club.pk)
        license_form.fields['sportsClub'].queryset = SportsClub.objects.filter(id__in=clubsPk)

    elif user.groups.filter(name__in=['Yonetim', 'Admin']):
        license_form.fields['sportsClub'].queryset = SportsClub.objects.all()

    if request.method == 'POST':
        if license_form.is_valid():
            license_form.save()
            messages.success(request, 'Lisans Başarıyla Güncellenmiştir.')
            return redirect('wushu:update-athletes', pk=athlete_pk)

        else:

            messages.warning(request, 'Alanları Kontrol Ediniz')

    return render(request, 'sporcu/sporcu-lisans-duzenle.html',
                  {'license_form': license_form, 'license': license})


@login_required
def sporcu_lisans_sil(request, pk, athlete_pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    if request.method == 'POST' and request.is_ajax():
        try:
            obj = License.objects.get(pk=pk)
            athlete = Athlete.objects.get(pk=athlete_pk)
            athlete.licenses.remove(obj)
            obj.delete()
            return JsonResponse({'status': 'Success', 'messages': 'save successfully'})
        except Level.DoesNotExist:
            return JsonResponse({'status': 'Fail', 'msg': 'Object does not exist'})

    else:
        return JsonResponse({'status': 'Fail', 'msg': 'Not a valid request'})


@login_required
def sporcu_kusak_listesi(request):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    login_user = request.user
    user = User.objects.get(pk=login_user.pk)

    if user.groups.filter(name='KulupUye'):
        clubuser = SportClubUser.objects.get(user=user)
        clubs = SportsClub.objects.filter(clubUser=clubuser)
        clubsPk = []
        for club in clubs:
            clubsPk.append(club.pk)
        belts = Level.objects.filter(athlete__licenses__sportsClub__in=clubsPk)
    elif user.groups.filter(name__in=['Yonetim', 'Admin']):
        belts = Level.objects.all().distinct()

    return render(request, 'sporcu/sporcu-kusak-listesi.html', {'belts': belts})


@login_required
def sporcu_lisans_listesi(request):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')
    login_user = request.user
    user = User.objects.get(pk=login_user.pk)

    if user.groups.filter(name='KulupUye'):
        clubuser = SportClubUser.objects.get(user=user)
        clubs = SportsClub.objects.filter(clubUser=clubuser)
        clubsPk = []
        for club in clubs:
            clubsPk.append(club.pk)
        licenses = License.objects.filter(athlete__licenses__sportsClub__in=clubsPk)
    elif user.groups.filter(name__in=['Yonetim', 'Admin']):
        licenses = License.objects.all().distinct()

    return render(request, 'sporcu/sporcu-lisans-listesi.html', {'licenses': licenses})


@login_required
def updateAthleteProfile(request, pk):
    perm = general_methods.control_access(request)

    if not perm:
        logout(request)
        return redirect('accounts:login')

    user = User.objects.get(pk=pk)
    directory_user = Athlete.objects.get(user=user)
    person = Person.objects.get(pk=directory_user.person.pk)
    communication = Communication.objects.get(pk=directory_user.communication.pk)
    user_form = DisabledUserForm(request.POST or None, instance=user)
    person_form = DisabledPersonForm(request.POST or None, request.FILES or None, instance=person)
    communication_form = DisabledCommunicationForm(request.POST or None, instance=communication)
    password_form = SetPasswordForm(request.user, request.POST)

    if request.method == 'POST':

        if user_form.is_valid() and communication_form.is_valid() and person_form.is_valid() and password_form.is_valid():

            user.username = user_form.cleaned_data['email']
            user.first_name = user_form.cleaned_data['first_name']
            user.last_name = user_form.cleaned_data['last_name']
            user.email = user_form.cleaned_data['email']
            user.set_password(password_form.cleaned_data['new_password1'])
            user.save()

            person_form.save()
            communication_form.save()
            password_form.save()

            messages.success(request, 'Sporcu Başarıyla Güncellenmiştir.')

            return redirect('wushu:sporcu-profil-guncelle')

        else:

            messages.warning(request, 'Alanları Kontrol Ediniz')

    return render(request, 'sporcu/sporcu-profil-guncelle.html',
                  {'user_form': user_form, 'communication_form': communication_form,
                   'person_form': person_form, 'password_form': password_form})
