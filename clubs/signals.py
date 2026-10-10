from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from clubs.models import ClubMembership,ClubRole,Club

@receiver(post_save, sender=ClubMembership)
def send_membership_confirmation(sender, instance, created, **kwargs):
    print(f"Signal triggered: send_membership_confirmation - created={created}, confirmed={instance.confirmed}")
    if created and not instance.confirmed:
        token = default_token_generator.make_token(instance.user)
        confirmation_link = f"{settings.FRONTEND_URL}/clubs/membership/confirm/{instance.id}/{token}/"
        
        subject = f"Confirm your membership for {instance.club.name}"
        message = f"Hi {instance.user.username},\nPlease confirm your membership by clicking this link: {confirmation_link}"
        recipient_list = [instance.user.email]
        
        try:
            print(f"Attempting to send email to {instance.user.email}")
            print(f"From: {settings.EMAIL_HOST_USER}")
            print(f"Subject: {subject}")
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Failed to send email to {instance.user.email}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {str(e)}")
            print(f"Please check your email settings and make sure your Gmail account allows less secure apps")

@receiver(post_save, sender=ClubMembership)
def assign_default_role(sender, instance, created, **kwargs):
    print(f"Signal triggered: assign_default_role - created={created}, has_role={bool(instance.role)}")
    if created and not instance.role:
        default_role = ClubRole.objects.filter(club=instance.club, role_name="Member").first()
        if default_role:
            instance.role = default_role
            instance.save()