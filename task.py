from celery import shared_task
from cis_task import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
import shortuuid

@shared_task(bind=True)
def create_users(self, number_of_users):
    print('*********************',User.objects.all())
    '''Creates multiple users into DB based upon given number of users'''
    random_suffixes = [shortuuid.uuid() for _ in range(int(number_of_users))]
    users = [
        User(username=f'user{suffix}', email=f'user{suffix}@mailinator.com')
        for suffix in random_suffixes
    ]
    User.objects.bulk_create(users)
    print('**********************',User.objects.all())
    return {"message": f"{number_of_users} users have been created."}



@shared_task(bind=True)
def send_mail_to_all_users(self, email_data):
    '''Sends customized email to all the users present in DB '''
    users = User.objects.all()
    mail_subject = email_data["mail_subject"]
    message =  email_data["message"]
    for user in users:
        to_email = user.email
        try:
            send_mail(
                subject = mail_subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[to_email],
                fail_silently=True,
            )
            print({"message": f"Email sent to {to_email}"})
        except Exception as e:
            print({"message": f"{e} : error occured while sending email to {to_email}"})
    
