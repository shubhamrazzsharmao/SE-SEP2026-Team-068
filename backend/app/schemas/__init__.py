"""Views (the V in MVC): Pydantic schemas that define what the API accepts and returns.

`*In` / `*Update` classes validate request bodies; `*Out` classes shape the JSON responses.
Import from here: `from app.schemas import CampaignOut`.
"""
from app.schemas.activity import ActivityOut
from app.schemas.brand import BrandIn, BrandOut, BrandUpdate
from app.schemas.brief import BriefIn, BriefOut, BriefUpdate
from app.schemas.campaign import CampaignIn, CampaignOut, MemberIn, MemberOut
from app.schemas.comment import CommentIn, CommentOut
from app.schemas.content import (ContentPieceDetail, ContentPieceOut, EditIn, GenerateOut,
                                  JobOut, VersionCheckOut, VersionOut)
from app.schemas.dashboard import CampaignCounts, DashboardOut, HealthOut, StatusCounts
from app.schemas.review import ApproveIn, RejectIn, RequestChangesIn, ReviewOut
from app.schemas.user import UserOut

__all__ = ["ActivityOut", "BrandIn", "BrandOut", "BrandUpdate", "BriefIn", "BriefOut", "BriefUpdate",
           "CampaignIn", "CampaignOut", "MemberIn", "MemberOut", "CommentIn", "CommentOut",
           "ContentPieceDetail", "ContentPieceOut", "EditIn", "GenerateOut", "JobOut", "VersionCheckOut", "VersionOut",
           "CampaignCounts", "DashboardOut", "HealthOut", "StatusCounts", "ApproveIn", "RejectIn",
           "RequestChangesIn", "ReviewOut", "UserOut"]
