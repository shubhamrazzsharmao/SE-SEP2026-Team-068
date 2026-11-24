import pytest

from app.enums import UserRole
from app.models import User
from tests.helpers import PRESENT


@pytest.mark.us("US13")
def test_piece_activity_records_who_did_what(api, users, generated):
    """The piece log lists generation, edit and approval with user, action and version"""
    api.patch(f"/content/{generated.blog}", users.bob, json={"body": "edited"})
    api.post(f"/content/{generated.blog}/approve", users.carol, json={"version_no": 2})
    api.check(api.get(f"/content/{generated.blog}/activity", users.dave), 200, **{
        "0.action": "generated", "0.user_name": "Bob Creator", "0.version_no": 1,
        "1.action": "edited", "1.version_no": 2, "1.user_name": "Bob Creator",
        "2.action": "approved", "2.user_name": "Carol Reviewer", "2.version_no": 2,
        "2.created_at": PRESENT})


@pytest.mark.us("US13", "US9")
def test_change_request_note_is_logged(api, users, generated):
    """Change-request notes and regenerations are logged"""
    api.post(f"/content/{generated.facebook}/request-changes", users.carol, json={"feedback": "Stronger CTA please."})
    api.check(api.get(f"/content/{generated.facebook}/activity", users.bob), 200, **{
        "1.action": "changes_requested", "1.detail.feedback": "Stronger CTA please.", "1.version_no": 1,
        "2.action": "regenerated", "2.version_no": 2})


@pytest.mark.us("US13", "US8")
def test_rejection_reason_is_logged(api, users, generated):
    """The rejection and its reason are logged"""
    api.post(f"/content/{generated.blog}/reject", users.carol, json={"reason": "Not suitable for our audience."})
    api.check(api.get(f"/content/{generated.blog}/activity", users.bob), 200, **{
        "1.action": "rejected", "1.detail.reason": "Not suitable for our audience."})


@pytest.mark.us("US13")
def test_outsider_cannot_read_piece_activity(api, users, generated):
    """Outsider gets 404 for a piece's log"""
    api.check(api.get(f"/content/{generated.blog}/activity", users.eve), 404, code="NOT_FOUND")


@pytest.mark.us("US13")
def test_owner_reads_campaign_activity(api, users, generated):
    """Owner sees the campaign log, newest first"""
    api.post(f"/content/{generated.blog}/approve", users.carol)
    api.check(api.get(f"/campaigns/{generated.campaign_id}/activity", users.alice), 200,
              **{"0.action": "approved", "0.user_name": "Carol Reviewer"})


@pytest.mark.us("US13")
def test_creator_cannot_read_campaign_activity(api, users, generated):
    """Creators cannot read the campaign-wide log"""
    api.check(api.get(f"/campaigns/{generated.campaign_id}/activity", users.bob), 403, code="FORBIDDEN")


@pytest.mark.us("US13")
def test_admin_reads_activity_without_membership(api, users, generated, db):
    """A global admin can read any campaign's log"""
    api.get("/me", users.eve)
    db.get(User, users.eve.id).role = UserRole.admin
    db.commit()
    api.check(api.get(f"/campaigns/{generated.campaign_id}/activity", users.eve), 200, **{"0.action": PRESENT})


@pytest.mark.us("US13")
def test_admin_gets_404_for_unknown_campaign(api, users, db):
    """Admin asking for a campaign that does not exist gets 404"""
    api.get("/me", users.eve)
    db.get(User, users.eve.id).role = UserRole.admin
    db.commit()
    api.check(api.get("/campaigns/9999/activity", users.eve), 404, code="NOT_FOUND")


@pytest.mark.us("US13")
def test_activity_log_is_read_only(api, users, generated):
    """There is no way to modify or delete log entries"""
    api.check(api.delete(f"/content/{generated.blog}/activity", users.alice), 405, code="METHOD_NOT_ALLOWED")
    api.check(api.post(f"/content/{generated.blog}/activity", users.alice, json={"action": "x"}), 405,
              code="METHOD_NOT_ALLOWED")
