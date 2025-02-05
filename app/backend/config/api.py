from ninja import NinjaAPI

from main.handlers import router as main_router


api = NinjaAPI(title="Astria API")

api.add_router("/main", main_router, tags=["Main"])
