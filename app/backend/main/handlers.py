from ninja import Router
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from dto.user import CreateUserDTO, UserDTO
from dto.err import ErrorDTO
from .models import TGUser


router = Router()


@router.get("/healthcheck")
def healthcheck(request):
    return {"msg": "Ok Ok"}


@router.post("/create", response={201: UserDTO, 400: ErrorDTO})
def create_user(request, create_user: CreateUserDTO):
    try:
        cln = TGUser.objects.create(**create_user.dict().get("user"))
    except IntegrityError as err:
        return 400, {"message": "such a tg user already exists", "err": err}
    return 201, cln
