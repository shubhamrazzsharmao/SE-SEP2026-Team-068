"""Controller for brands (clients).

HTTP only: validated input comes in (app.schemas), brand_service does the work, a view goes out.
"""
from fastapi import APIRouter

from app.controllers.deps import DB, CurrentUser
from app.core.errors import errs
from app.schemas import BrandIn, BrandOut, BrandUpdate
from app.services import brand_service

router = APIRouter(prefix="/brands", tags=["Brands"])


@router.post("", response_model=BrandOut, status_code=201, responses=errs(401, 409, 422),
             openapi_extra={"x-user-stories": ["US5", "US11"]})
def create_brand(body: BrandIn, db: DB, user: CurrentUser):
    """Create a brand (the client and its voice): tone, preferred terms and terms to avoid.

    The caller becomes the brand owner. Brand names are unique per owner.

    **User stories:** US5 (define brand guidelines), US11 (client -> campaign hierarchy).
    """
    return brand_service.create(db, user, body)


@router.get("", response_model=list[BrandOut], responses=errs(401),
            openapi_extra={"x-user-stories": ["US5", "US11"]})
def list_brands(db: DB, user: CurrentUser):
    """List brands the caller owns or can see through a campaign membership.

    **User stories:** US5, US11.
    """
    return brand_service.list_visible(db, user)


@router.get("/{brand_id}", response_model=BrandOut, responses=errs(401, 404),
            openapi_extra={"x-user-stories": ["US5"]})
def get_brand(brand_id: int, db: DB, user: CurrentUser):
    """Get one brand. Returns 404 if the caller neither owns it nor belongs to a campaign that uses it.

    **User stories:** US5.
    """
    return brand_service.get_visible(db, brand_id, user)


@router.patch("/{brand_id}", response_model=BrandOut, responses=errs(401, 403, 404, 409, 422),
              openapi_extra={"x-user-stories": ["US5"]})
def update_brand(brand_id: int, body: BrandUpdate, db: DB, user: CurrentUser):
    """Edit brand guidelines. Allowed for the brand owner and for a `brand_manager` of a
    campaign that uses the brand.

    Changes apply only to content generated afterwards; existing versions are untouched.

    **User stories:** US5 (define brand guidelines).
    """
    return brand_service.update(db, brand_id, user, body)
