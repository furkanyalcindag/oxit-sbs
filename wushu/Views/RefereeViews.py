from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import render, redirect

from wushu.Forms.CommunicationForm import CommunicationForm
from wushu.Forms.UserForm import UserForm
from wushu.Forms.PersonForm import PersonForm
from wushu.models import Judge


@login_required
def return_add_referee(request):
    user_form = UserForm()
    person_form = PersonForm()
    communication_form = CommunicationForm()

    if request.method == 'POST':
        x = User.objects.latest('id')

        data = request.POST.copy()
        data['username'] = data['email']
        user_form = UserForm(data)
        person_form = PersonForm(request.POST, request.FILES)
        communication_form = CommunicationForm(request.POST, request.FILES)

        if user_form.is_valid() and person_form.is_valid() and communication_form.is_valid():
            user = user_form.save(commit=False)
            person = person_form.save(commit=False)
            communication = communication_form.save(commit=False)
            group = Group.objects.get(name='Hakem')
            user2 = user_form.save()
            password = User.objects.make_random_password()
            user.set_password(password)
            user2.groups.add(group)
            user.save()
            person.save()
            communication.save()

            judge = Judge(user=user, person=person, communication=communication)

            judge.save()

            subject, from_email, to = 'WUSHU - Hakem Bilgi Sistemi Kullanıcı Giriş Bilgileri', 'kayit@oxityazilim.com', user2.email
            text_content = 'Aşağıda ki bilgileri kullanarak sisteme giriş yapabilirsiniz.'
            html_content = '<p> <strong>Site adresi: </strong> <a href="https://www.twf.gov.tr/"></a>https://www.twf.gov.tr/</p>'
            html_content = html_content + '<p><strong>Kullanıcı Adı:  </strong>' + user2.username + '</p>'
            html_content = html_content + '<p><strong>Şifre: </strong>' + password + '</p>'
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            messages.success(request, 'Hakem Başarıyla Kayıt Edilmiştir.')

            return redirect('wushu:hakem-ekle')

        else:

            messages.warning(request, 'Alanları Kontrol Ediniz')

    return render(request, 'hakem/hakem-ekle.html',
                  {'user_form': user_form, 'person_form': person_form, 'communication_form': communication_form})


@login_required
def return_referees(request):
    return render(request, 'hakem/hakemler.html')
