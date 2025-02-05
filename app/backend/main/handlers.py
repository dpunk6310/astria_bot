from ninja import Router
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist


router = Router()


@router.get("/healthcheck")
def healthcheck(request, ):
    return {"msg": "Ok Ok"}
