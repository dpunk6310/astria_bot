from django.contrib import admin
# from django_celery_beat.models import (
#     PeriodicTask, 
#     IntervalSchedule, 
#     CrontabSchedule, 
#     SolarSchedule
# )

from django.contrib.admin import ModelAdmin, TabularInline

from .models import (
    TGUser, 
    Image, 
    Payment, 
    Tune, 
    PriceList, 
    Category,
    Promt,
    Newsletter
)


@admin.register(Image)
class ImageAdmin(ModelAdmin):
    list_display = [
        "id", "tg_user", "img_path"
    ]
    list_display_links = ["tg_user",]
    search_fields = [
        "tg_user",
    ]
    save_as = True
    save_on_top = True
    
    
@admin.register(Newsletter)
class NewsletterAdmin(ModelAdmin):
    list_display = [
        "id", "title", "delay_hours", "created_at"
    ]
    list_display_links = ["title",]
    search_fields = [
        "title",
    ]
    save_as = True
    save_on_top = True
    
    
@admin.register(PriceList)
class PriceListAdmin(ModelAdmin):
    list_display = [
        "id", "price", "count", "learn_model", "sale", "type_price_list"
    ]
    list_display_links = ["price", "type_price_list", "count"]
    search_fields = [
        "price",
    ]
    save_as = True
    save_on_top = True
    
    
@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = [
        "id", "payment_id", "tg_user_id", "amount", "is_first_payment", "status"
    ]
    list_display_links = ["payment_id",]
    search_fields = [
        "payment_id",
    ]
    save_as = True
    save_on_top = True
    
    
@admin.register(Tune)
class TuneAdmin(ModelAdmin):
    list_display = [
        "id", "tune_id", "tg_user_id"
    ]
    list_display_links = ["tune_id",]
    search_fields = [
        "tune_id", "tg_user_id"
    ]
    save_as = True
    save_on_top = True


@admin.register(TGUser)
class TGUserAdmin(ModelAdmin):
    list_display = [
        "id", "tg_user_id", "username", "first_name", "last_name", "god_mod", "is_learn_model", "has_purchased"
    ]
    list_display_links = ["tg_user_id", "username",]
    search_fields = [
        "tg_user_id", "username", "first_name", "referal"
    ]
    save_as = True
    save_on_top = True


class PromtInline(TabularInline):  # Или admin.StackedInline для другого стиля отображения
    model = Promt
    extra = 1

    
@admin.register(Promt)
class PromtAdmin(ModelAdmin):
    list_display = [
        "id", "category",
    ]
    list_display_links = ["category"]
    save_as = True
    save_on_top = True
    
    
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = [
        "id", "name", "slug", "gender"
    ]
    list_display_links = ["name", "slug",]
    search_fields = [
        "name", "slug", "gender",
    ]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PromtInline]
    save_as = True
    save_on_top = True
    


# admin.site.register(PeriodicTask)
# admin.site.register(IntervalSchedule)
# admin.site.register(CrontabSchedule)
# admin.site.register(SolarSchedule)
