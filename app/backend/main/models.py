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
    count_generations = models.PositiveIntegerField(
        verbose_name="Кол-во генераций", default=0
    )
    is_learn_model = models.BooleanField(
        verbose_name="Использование обучения модели",
        default=True
    )
    god_mod = models.BooleanField(verbose_name="Режим бога", default=False)
    referal = models.CharField(verbose_name="Реферал", max_length=30, null=True, blank=True)

    def __str__(self):
        return str(self.tg_user_id)
    
    class Meta:
        verbose_name = "TG User"
        verbose_name_plural = "TG user"
        db_table = "tg_users"
        
        
class PriceList(models.Model):
    price = models.CharField(verbose_name="Цена", max_length=20)
    count = models.PositiveIntegerField(verbose_name="Кол-во", default=20)
    learn_model = models.BooleanField(verbose_name="Обучение модели", default=False)
    sale = models.CharField(verbose_name="Скидка", null=True, blank=True, default="", help_text="Например: 30%")
    
    def __str__(self):
        return f"{self.price} - {self.count}"
    
    class Meta:
        verbose_name = "Price List"
        verbose_name_plural = "Prices List"
        db_table = "prices_list"
    

class Image(models.Model):
    tg_user = models.ForeignKey(
        TGUser, 
        on_delete=models.CASCADE, 
        related_name="images", 
        verbose_name="TG User"
    )
    img_path = models.CharField(
        max_length=500, 
        null=True, 
        blank=True, 
        verbose_name="Image path",
    )
    
    def __str__(self):
        return str(self.tg_user)
    
    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"
        db_table = "images"
        
        
class Tune(models.Model):
    tg_user_id = models.CharField(
        max_length=30,
        verbose_name="TG User ID"
    )
    tune_id = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Tune ID"
    )
    gender = models.CharField(verbose_name="Пол", max_length=20)
    
    def __str__(self):
        return str(self.tune_id)
    
    class Meta:
        verbose_name = "Tune"
        verbose_name_plural = "Tunes"
        db_table = "tunes"
        
        
class Payment(models.Model):
    tg_user_id = models.CharField(
        max_length=30,
        verbose_name="TG User ID"
    )
    payment_id = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Payment ID"
    )
    status = models.BooleanField(verbose_name="Status", default=False)
    сount_generations = models.PositiveIntegerField(
        verbose_name="Кол-во генераций", default=0
    )
    amount = models.CharField(max_length=20, verbose_name="Сумма")
    learn_model = models.BooleanField(verbose_name="Обучение модели", default=False)
    is_first_payment = models.BooleanField(verbose_name="Первый платеж", default=False)
    
    def __str__(self):
        return str(self.payment_id)
    
    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        db_table = "payments"
