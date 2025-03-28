from django.db import models
from django.db.models import Sum, Count
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models.functions import Cast
from pytils.translit import slugify

GENDER_CHOICES = [
    ('man', 'man'),
    ('woman', 'woman'),
]

TYPE_PRICE_CHOICES = [
    ('photo', 'photo'),
    ('video', 'video'),
    ('promo', 'promo'),
]


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
    count_video_generations = models.PositiveIntegerField(
        verbose_name="Кол-во генераций видео", default=0
    )
    is_learn_model = models.BooleanField(
        verbose_name="Использование обучения модели",
        default=True
    )
    god_mod = models.BooleanField(verbose_name="Режим бога", default=False)
    photo_from_photo = models.BooleanField(verbose_name="Режим Фото по фото", default=False)
    referal = models.CharField(verbose_name="Реферал", max_length=30, null=True, blank=True)
    effect = models.CharField(verbose_name="Выбранный фильтр(эффект)", max_length=100, null=True, blank=True)
    tune_id = models.CharField(verbose_name="Выбранный TUNE", max_length=30, null=True, blank=True)
    god_mod_text = models.TextField(verbose_name="Текст промта", null=True, blank=True)
    category = models.CharField(verbose_name="Выбраная категория", max_length=300, null=True, blank=True)
    gender = models.CharField(verbose_name="Выбраный пол", max_length=300, null=True, blank=True)
    last_activity = models.DateTimeField(verbose_name="Последняя активность", auto_now=True)
    has_purchased = models.BooleanField(verbose_name="Сделал покупку", default=True)
    subscribe = models.DateField(verbose_name="Подписка до", null=True, blank=True)
    maternity_payment_id = models.CharField(
        verbose_name="Материнский платежный ID", max_length=200, null=True, blank=True
    )
    sent_messages = models.JSONField(default=[0], verbose_name="Отправленные рассылки")
    
    referral_count = models.PositiveIntegerField(
        verbose_name="Количество рефералов", 
        default=0
    )
    reward_generations = models.PositiveIntegerField(
        verbose_name="Количество генераций от рефералов", 
        default=0
    )
    referral_purchases = models.PositiveIntegerField(
        verbose_name="Количество покупок рефералов", 
        default=0
    )
    referral_purchases_amount = models.DecimalField(
        verbose_name="Сумма покупок реферала", 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    user_purchases_count = models.PositiveIntegerField(
        verbose_name="Количество покупок пользователя", 
        default=0
    )
    user_purchases_amount = models.DecimalField(
        verbose_name="Сумма покупок пользователя", 
        max_digits=10, 
        decimal_places=2, 
        default=0
    )
    attempt = models.PositiveIntegerField(verbose_name="Попытка", default=0)
    
    def __str__(self):
        return str(self.tg_user_id)
    
    class Meta:
        verbose_name = "TG User"
        verbose_name_plural = "TG user"
        db_table = "tg_users"
        
        
class Newsletter(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название рассылки")
    slug = models.CharField(max_length=255, verbose_name="Уникальный slug", unique=True)
    message_text = models.TextField(verbose_name="Текст сообщения")
    delay_hours = models.FloatField(verbose_name="Задержка в часах", null=True, blank=True)
    photo = models.ImageField(verbose_name="Изображение", null=True, blank=True, upload_to="media/newsletter")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    squeeze = models.BooleanField(verbose_name="Дожимка", default=False)

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        db_table = "newsletters"
        
        
class Category(models.Model):
    name = models.CharField(verbose_name="Название", max_length=300)
    slug = models.SlugField(verbose_name="Slug", max_length=400, unique=True)
    gender = models.CharField(verbose_name="Пол", max_length=20, choices=GENDER_CHOICES)
    
    def save(self, *args, **kwargs):
        base_slug = slugify(self.name)
        self.slug = f"category_{self.gender}_{base_slug}"
        counter = 1
        while Category.objects.filter(slug=self.slug).exists():
            self.slug = f"category_{self.gender}_{base_slug}-{counter}"
            counter += 1
        super(Category, self).save(*args, **kwargs)
    
    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        db_table = "categories"
        
        
class Promt(models.Model):
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name="promts", 
        verbose_name="Категория",
    )
    text = models.TextField(verbose_name="Текст", unique=True)
    
    def __str__(self):
        return str(self.category.name)
    
    def save(self, *args, **kwargs):
        self.text = f"sks {self.category.gender} {self.text}"
        super(Promt, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Promt"
        verbose_name_plural = "Promts"
        db_table = "promts"
          
        
class PriceList(models.Model):
    price = models.CharField(verbose_name="Цена", max_length=20)
    count = models.PositiveIntegerField(verbose_name="Кол-во", default=1)
    count_video = models.PositiveIntegerField(verbose_name="Кол-во видео", default=1, null=True, blank=True)
    learn_model = models.BooleanField(verbose_name="Обучение модели", default=False)
    sale = models.CharField(verbose_name="Скидка", null=True, blank=True, default="", help_text="Например: -30%")
    type_price_list = models.CharField(
        verbose_name="Тип списка цен", 
        choices=TYPE_PRICE_CHOICES, 
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return f"{self.price} - {self.count}"
    
    class Meta:
        verbose_name = "Price List"
        verbose_name_plural = "Prices List"
        db_table = "prices_list"
    
        
class TGImage(models.Model):
    tg_user = models.ForeignKey(
        TGUser, 
        on_delete=models.CASCADE, 
        related_name="tg_images", 
        verbose_name="TG User"
    )
    img_hash = models.CharField(
        max_length=1000,
        unique=True,
        verbose_name="Image hash",
    )
    
    def __str__(self):
        return str(self.tg_user)
    
    class Meta:
        verbose_name = "TG Image"
        verbose_name_plural = "TG Images"
        db_table = "tg_images"
        
        
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
    name = models.CharField(verbose_name="Название", max_length=20, null=True, blank=True)
    
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
    description = models.CharField(verbose_name="Описание", null=True, blank=True)
    status = models.BooleanField(verbose_name="Status", default=False)
    сount_generations = models.PositiveIntegerField(
        verbose_name="Кол-во генераций", default=0
    )
    count_video_generations = models.PositiveIntegerField(
        verbose_name="Кол-во генераций видео", default=0
    )
    count_generations_for_gift = models.PositiveIntegerField(
        verbose_name="Кол-во генераций фото для подарка", default=0
    )
    count_generations_video_for_gift = models.PositiveIntegerField(
        verbose_name="Кол-во генераций видео для подарка", default=0
    )
    promo = models.BooleanField(verbose_name="Промо", default=False)
    amount = models.CharField(max_length=20, verbose_name="Сумма")
    learn_model = models.BooleanField(verbose_name="Обучение модели", default=False)
    is_first_payment = models.BooleanField(verbose_name="Первый платеж", default=False)
    created_at = models.DateTimeField(
        verbose_name="Создан", auto_now_add=True, null=True, blank=True,
    )
    subscription_renewal = models.BooleanField(verbose_name="Продление подписки", default=False)
    
    def __str__(self):
        return str(self.payment_id)
    
    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        db_table = "payments"
        
        
class Promocode(models.Model):
    tg_user_id = models.CharField(
        max_length=30,
        verbose_name="TG User ID"
    )
    code = models.CharField(max_length=200, verbose_name="Код", unique=True)
    status = models.BooleanField(verbose_name="Status", default=True)
    created_at = models.DateTimeField(
        verbose_name="Создан", auto_now_add=True, null=True, blank=True,
    )
    count_generations = models.PositiveIntegerField(default=0, verbose_name="Кол-во генераций фото")
    count_video_generations = models.PositiveIntegerField(default=0, verbose_name="Кол-во генераций видео")
    is_learn_model = models.BooleanField(default=False, verbose_name="Обучение модели")

    def __str__(self):
        return str(self.code)
    
    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
        db_table = "promocodes"
