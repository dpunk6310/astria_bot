from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline

from .models import (
    TGUser, 
    Payment, 
    Tune, 
    PriceList, 
    Category,
    Promt,
    Newsletter,
    TGImage,
    Promocode
)

    
@admin.register(TGImage)
class TGImageAdmin(ModelAdmin):
    list_display = [
        "id", "tg_user", "img_hash"
    ]
    list_display_links = ["tg_user", "img_hash"]
    search_fields = [
        "tg_user", "img_hash"
    ]
    save_as = True
    save_on_top = True
    
    
@admin.register(Newsletter)
class NewsletterAdmin(ModelAdmin):
    list_display = [
        "id", "title", "slug", "delay_hours", "squeeze", "created_at"
    ]
    list_display_links = ["title", "slug"]
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
        "id", "payment_id", "tg_user_id", "amount", "is_first_payment", "status", "description"
    ]
    list_display_links = ["payment_id",]
    search_fields = [
        "payment_id", "tg_user_id"
    ]
    save_as = True
    save_on_top = True
    
    
@admin.register(Promocode)
class PromocodeAdmin(ModelAdmin):
    list_display = [
        "id", "tg_user_id", "code", "status", "created_at"
    ]
    list_display_links = ["tg_user_id", "code"]
    search_fields = [
        "tg_user_id", "code"
    ]
    save_as = True
    save_on_top = True
    
    
@admin.register(Tune)
class TuneAdmin(ModelAdmin):
    list_display = [
        "id", "tune_id", "tg_user_id", "name"
    ]
    list_display_links = ["tune_id", "tg_user_id", "name"]
    search_fields = [
        "tune_id", "tg_user_id"
    ]
    save_as = True
    save_on_top = True


@admin.register(TGUser)
class TGUserAdmin(ModelAdmin):
    list_display = [
        "id", 
        "tg_user_id", 
        "username", 
        "first_name", 
        "last_name", 
        "god_mod", 
        "is_learn_model", 
        "has_purchased",
        "subscribe",
        "referral_count",
        "reward_generations",
        "referral_purchases",
        "user_purchases_count",
        "user_purchases_amount",
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
    # prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["slug"]
    inlines = [PromtInline]
    save_as = True
    save_on_top = True
    


# admin.site.register(PeriodicTask)
# admin.site.register(IntervalSchedule)
# admin.site.register(CrontabSchedule)
# admin.site.register(SolarSchedule)
