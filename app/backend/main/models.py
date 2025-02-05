from django.db import models


class TGUser(models.Model):
    tg_user_id = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="TG UserID"
    )
    first_name = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name="First name",
    )
    last_name = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name="Last name",
    )
    username = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name="Username",
        unique=True,
    )
    
    def __str__(self):
        return self.tg_user_id
    
    class Meta:
        verbose_name = "TG User"
        verbose_name_plural = "TG user"
        db_table = "tg_users"
