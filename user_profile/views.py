from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, authenticate 
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import  force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage


from django_registration.views import RegistrationView
from django_registration.forms import RegistrationFormUniqueEmail


from .tokens import account_activation_token
from .forms import SignupForm
# Create your views here.


class RegistrationViewUniqueEmail(RegistrationView):
  form_class = RegistrationFormUniqueEmail





def signup(request):
	if request.method == 'POST':
		form = SignupForm( request.POST )

		if form.is_valid():
			user = form.save( commit = False )
			user.us_active = False
			user.save()
			current_site = get_current_site(request)
			mail_subject = 'Активировать твой аккаунт.' # Тема отправки письма
			message = render_to_string('acc_active_email.html', {
				'user': user,
				'domain': current_site.domain,
				'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
				'token': account_activation_token.make_token(user),
				})
			to_email = form.cleaned_data.get('email')
			email = EmailMessage( mail_subject, message, to = [to_email])
			email.send()

			return HttpResponse('На вашу почту отправленно письмо для окончания регистрации')
	else:
		form = SignupForm()

	return render(request, 'signup.html', {'form': form})


def activate( request, uidb64, token ):
	try:
		uid = urlsafe_base64_decode(uidb64).decode()
		user = User.objects.get(pk = uid)

	except(TypeError, ValueError, OverflowError, User.DoesNotExist ):
		user = None

	if user is not None and account_activation_token.check_token(user,token):
		user.is_active = True
		user.save()
		login( request, user)
		return redirect('courses:home_page')

	else:
		return HttpResponse('Данная ссылка не действительна ')