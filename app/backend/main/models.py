from django.db import models
from django.utils.text import slugify


GENDER_CHOICES = [
    ('man', 'man'),
    ('woman', 'woman'),
]

TYPE_PRICE_CHOICES = [
    ('photo', 'photo'),
    ('video', 'video'),
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
    referal = models.CharField(verbose_name="Реферал", max_length=30, null=True, blank=True)
    effect = models.CharField(verbose_name="Выбранный фильтр(эффект)", max_length=100, null=True, blank=True)
    tune_id = models.CharField(verbose_name="Выбранный TUNE", max_length=30, null=True, blank=True)
    god_mod_text = models.TextField(verbose_name="Текст промта", null=True, blank=True)
    category = models.CharField(verbose_name="Выбраная категория", max_length=300, null=True, blank=True)
    gender = models.CharField(verbose_name="Выбраный пол", max_length=300, null=True, blank=True)
    last_activity = models.DateTimeField(verbose_name="Последняя активность", auto_now=True)
    has_purchased = models.BooleanField(verbose_name="Сделал покупку", default=True)
    
    sent_messages = models.JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return str(self.tg_user_id)
    
    class Meta:
        verbose_name = "TG User"
        verbose_name_plural = "TG user"
        db_table = "tg_users"
        
        
class Newsletter(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название рассылки")
    message_text = models.TextField(verbose_name="Текст сообщения")
    delay_hours = models.FloatField(verbose_name="Задержка в часах", null=True, blank=True)
    # button = models.CharField(verbose_name="Название кнопки", null=True, blank=True)
    # button_data = models.CharField(verbose_name="URL или Callback для кнопки", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")

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
        self.slug = f"category_{self.gender}_{self.slug}"
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
    text = models.TextField(verbose_name="Текст")
    
    def __str__(self):
        return str(self.category.name)
    
    class Meta:
        verbose_name = "Promt"
        verbose_name_plural = "Promts"
        db_table = "promts"
          
        
class PriceList(models.Model):
    price = models.CharField(verbose_name="Цена", max_length=20)
    count = models.PositiveIntegerField(verbose_name="Кол-во", default=20)
    learn_model = models.BooleanField(verbose_name="Обучение модели", default=False)
    sale = models.CharField(verbose_name="Скидка", null=True, blank=True, default="", help_text="Например: 30%")
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
    count_video_generations = models.PositiveIntegerField(
        verbose_name="Кол-во генераций видео", default=0
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
