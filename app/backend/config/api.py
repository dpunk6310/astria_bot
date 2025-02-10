from ninja import NinjaAPI

from main.handlers import router as main_router


api = NinjaAPI(title="Pingvin API", docs_url="/hdfgisgfyusdgfuysdgfsgjhfwdgfgfgwiufgwgfgfiuguigwifgwifg")

api.add_router("/main", main_router, tags=["Main"])
