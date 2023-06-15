from django.db.models.signals import post_save ,pre_save
from django.dispatch import receiver

from accounts.models import User, UserProfile

@receiver(post_save,sender=User)  
def post_save_create_profile_reciever(sender,instance,created,**kwargs):
    print(created)
    if created:
        UserProfile.objects.create(user=instance)
        # print('user profile is created')
    else:
        try:
            profile=UserProfile.objects.get(user=instance)
            profile.save()
        except UserProfile.DoesNotExist:
            # creaate the user profile if not exit
            UserProfile.objects.create(user=instance)
            # print('unot exit but created one')
        # print('user is updates')

# post_save.connect(post_save_create_profile_reciever,sender=User)

@receiver(pre_save,sender=User)
def pre_save_profile_receiver(sender,instance,**kwargs):
    pass
    # print(instance.username,'this user is being save')