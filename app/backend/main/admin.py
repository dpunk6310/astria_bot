from django.contrib import admin

from unfold.admin import ModelAdmin

from .models import TGUser, Image, Payment, Tune, PriceList


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
    
    
@admin.register(PriceList)
class PriceListAdmin(ModelAdmin):
    list_display = [
        "id", "price", "count", "learn_model"
    ]
    list_display_links = ["price",]
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
        "tune_id",
    ]
    save_as = True
    save_on_top = True


@admin.register(TGUser)
class TGUserAdmin(ModelAdmin):
    list_display = [
        "id", "tg_user_id", "username", "first_name", "last_name", "god_mod", "is_learn_model",
    ]
    list_display_links = ["tg_user_id", "username",]
    search_fields = [
        "tg_user_id", "username",
    ]
    save_as = True
    save_on_top = True
