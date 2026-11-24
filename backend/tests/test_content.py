import pytest

from app.models import ActivityLog, ContentVersion
from tests.helpers import PRESENT


# ---------------------------------------------------------------- US10: status tracking
@pytest.mark.us("US10")
def test_filter_content_by_status(api, users, generated):
    """Filter a campaign's content by status"""
    api.post(f"/content/{generated.blog}/approve", users.carol)
    api.post(f"/content/{generated.linkedin}/reject", users.carol, json={"reason": "Wording is off-brand."})
    approved = api.check(api.get(f"/campaigns/{generated.campaign_id}/content", users.bob,
                                 params={"status": "approved"}), 200, **{"0.platform": "blog"})
    api.verify("one approved piece", len(approved), 1, api="GET /api/v1/campaigns/{campaign_id}/content")
    api.check(api.get(f"/campaigns/{generated.campaign_id}/content", users.bob, params={"status": "rejected"}),
              200, **{"0.platform": "linkedin", "0.rejection_reason": "Wording is off-brand."})
    pending = api.get(f"/campaigns/{generated.campaign_id}/content", users.bob, params={"status": "pending_review"})
    api.verify("two pending pieces", len(pending.json()), 2, api="GET /api/v1/campaigns/{campaign_id}/content")


@pytest.mark.us("US10")
def test_filter_content_by_platform(api, users, generated):
    """Filter a campaign's content by platform"""
    body = api.check(api.get(f"/campaigns/{generated.campaign_id}/content", users.bob,
                             params={"platform": "instagram"}), 200, **{"0.platform": "instagram"})
    api.verify("one instagram piece", len(body), 1, api="GET /api/v1/campaigns/{campaign_id}/content")


@pytest.mark.us("US10")
def test_invalid_status_filter_rejected(api, users, generated):
    """Unknown status value is a validation error"""
    api.check(api.get(f"/campaigns/{generated.campaign_id}/content", users.bob, params={"status": "published"}),
              422, code="VALIDATION_ERROR")


@pytest.mark.us("US10", "US11")
def test_outsider_cannot_list_content(api, users, generated):
    """Outsider gets 404 when listing a campaign's content"""
    api.check(api.get(f"/campaigns/{generated.campaign_id}/content", users.eve), 404, code="NOT_FOUND")


@pytest.mark.us("US6")
def test_piece_detail_includes_brief_and_versions(api, users, generated):
    """Reviewer opens a piece next to its brief"""
    api.check(api.get(f"/content/{generated.blog}", users.carol), 200, brief__topic="Spring Compost Kit",
              brief__key_messages=PRESENT, versions__0__version_no=1, current_version__version_no=1)


@pytest.mark.us("US6")
def test_outsider_cannot_read_piece(api, users, generated):
    """Outsider gets 404 for a piece"""
    api.check(api.get(f"/content/{generated.blog}", users.eve), 404, code="NOT_FOUND")


@pytest.mark.us("US9")
def test_version_history_is_ordered(api, users, generated):
    """Versions come back oldest first"""
    api.patch(f"/content/{generated.blog}", users.bob, json={"body": "second"})
    api.check(api.get(f"/content/{generated.blog}/versions", users.carol), 200,
              **{"0.version_no": 1, "0.origin": "ai_generated", "1.version_no": 2, "1.origin": "human_edit"})


# ---------------------------------------------------------------- editing
@pytest.mark.us("US6", "US13")
def test_edit_creates_new_version(api, users, generated):
    """An edit is saved as a new human_edit version"""
    api.check(api.patch(f"/content/{generated.blog}", users.bob, json={"body": "My improved blog text"}), 200,
              status="pending_review", current_version__version_no=2, current_version__origin="human_edit",
              current_version__body="My improved blog text", current_version__created_by=str(users.bob.id))


@pytest.mark.us("US6")
def test_editing_approved_piece_requires_new_approval(api, users, generated):
    """Editing an approved piece sends it back to pending review"""
    api.post(f"/content/{generated.blog}/approve", users.carol)
    api.check(api.patch(f"/content/{generated.blog}", users.bob, json={"body": "Changed after approval"}), 200,
              status="pending_review", current_version__version_no=2)


@pytest.mark.us("US6")
def test_edit_requires_body(api, users, generated):
    """Edit with an empty body is refused"""
    api.check(api.patch(f"/content/{generated.blog}", users.bob, json={"body": "  "}), 422,
              code="VALIDATION_ERROR", errors__0__field="body")


@pytest.mark.us("US6")
def test_brand_manager_cannot_edit_content(api, users, generated):
    """Brand managers cannot edit content"""
    api.check(api.patch(f"/content/{generated.blog}", users.dave, json={"body": "x"}), 403, code="FORBIDDEN")


# ---------------------------------------------------------------- delete with confirmation
@pytest.mark.us("US11")
def test_delete_requires_confirmation(api, users, generated):
    """Deleting without the confirmation flag is refused"""
    api.check(api.delete(f"/content/{generated.blog}", users.bob), 400, code="CONFIRMATION_REQUIRED")
    api.check(api.get(f"/content/{generated.blog}", users.bob), 200, status="pending_review")


@pytest.mark.us("US11", "US13")
def test_confirmed_delete_hides_piece_but_keeps_history(api, users, generated, db):
    """Confirmed delete hides the piece; versions and log are kept"""
    api.check(api.delete(f"/content/{generated.blog}", users.bob, params={"confirm": "true"}), 204)
    api.check(api.get(f"/content/{generated.blog}", users.bob), 404, code="NOT_FOUND")
    listing = api.get(f"/campaigns/{generated.campaign_id}/content", users.bob).json()
    api.verify("deleted piece is not listed", generated.blog in [p["id"] for p in listing], False,
               api="GET /api/v1/campaigns/{campaign_id}/content")
    api.verify("version rows are kept", db.query(ContentVersion).filter_by(piece_id=generated.blog).count(), 1)
    api.verify("deletion is logged", db.query(ActivityLog).filter_by(piece_id=generated.blog, action="deleted").count(), 1)


@pytest.mark.us("US11")
def test_reviewer_cannot_delete(api, users, generated):
    """Reviewers cannot delete content"""
    api.check(api.delete(f"/content/{generated.blog}", users.carol, params={"confirm": "true"}), 403, code="FORBIDDEN")


# ---------------------------------------------------------------- comments (client/reviewer discussion)
@pytest.mark.us("US6", "US8")
def test_member_comments_on_piece(api, users, generated):
    """Any member can comment on a piece"""
    api.check(api.post(f"/content/{generated.blog}/comments", users.carol, json={"body": "Please cite the source."}),
              201, body="Please cite the source.", author_name="Carol Reviewer", user_id=str(users.carol.id))
    api.check(api.post(f"/content/{generated.blog}/comments", users.bob, json={"body": "Added in the next draft."}), 201)
    api.check(api.get(f"/content/{generated.blog}/comments", users.dave), 200,
              **{"0.author_name": "Carol Reviewer", "1.author_name": "Bob Creator"})


@pytest.mark.us("US6")
def test_empty_comment_rejected(api, users, generated):
    """Blank comment is refused"""
    api.check(api.post(f"/content/{generated.blog}/comments", users.carol, json={"body": "   "}), 422,
              code="VALIDATION_ERROR", errors__0__field="body")


@pytest.mark.us("US6")
def test_outsider_cannot_comment(api, users, generated):
    """Outsider cannot comment or read comments"""
    api.check(api.post(f"/content/{generated.blog}/comments", users.eve, json={"body": "hi"}), 404, code="NOT_FOUND")
    api.check(api.get(f"/content/{generated.blog}/comments", users.eve), 404, code="NOT_FOUND")


# ---------------------------------------------------------------- dashboard
@pytest.mark.us("US10")
def test_dashboard_counts(api, users, generated):
    """Dashboard counts pieces per status, in total and per campaign"""
    api.post(f"/content/{generated.blog}/approve", users.carol)
    api.post(f"/content/{generated.linkedin}/reject", users.carol, json={"reason": "Wording is off-brand."})
    api.check(api.get("/dashboard", users.bob), 200, totals__approved=1, totals__rejected=1,
              totals__pending_review=2, campaigns__0__counts__approved=1,
              campaigns__0__campaign_id=generated.campaign_id)


@pytest.mark.us("US10")
def test_dashboard_for_user_without_campaigns(api, users):
    """A user without campaigns gets an empty dashboard"""
    api.check(api.get("/dashboard", users.eve), 200, totals__pending_review=0, campaigns=[])
