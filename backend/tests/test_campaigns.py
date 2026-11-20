import uuid

import pytest

from tests.helpers import PRESENT


@pytest.mark.us("US11")
def test_create_campaign(api, users, world):
    """Create a campaign under an own brand; the creator becomes owner"""
    r = api.post("/campaigns", users.alice, json={"brand_id": world.brand_id, "name": "Autumn Sale"})
    api.check(r, 201, name="Autumn Sale", my_role="owner", brand_name="GreenLeaf Organics")


@pytest.mark.us("US11")
def test_create_campaign_with_foreign_brand_fails(api, users, world):
    """Cannot create a campaign on somebody else's brand"""
    api.get("/me", users.eve)
    r = api.post("/campaigns", users.eve, json={"brand_id": world.brand_id, "name": "Hijack"})
    api.check(r, 404, code="NOT_FOUND")


@pytest.mark.us("US11")
def test_create_campaign_requires_name(api, users, world):
    """Campaign without a name is rejected"""
    api.check(api.post("/campaigns", users.alice, json={"brand_id": world.brand_id}), 422,
              code="VALIDATION_ERROR", errors__0__field="name")


@pytest.mark.us("US11")
def test_users_only_see_their_campaigns(api, users, world):
    """Members list their campaign with their role; outsiders see nothing"""
    api.check(api.get("/campaigns", users.carol), 200, **{"0.my_role": "reviewer", "0.id": world.campaign_id})
    api.check(api.get("/campaigns", users.eve), 200, whole=[])


@pytest.mark.us("US11")
def test_non_member_gets_404_for_campaign(api, users, world):
    """Non-member cannot see that a campaign exists"""
    api.check(api.get(f"/campaigns/{world.campaign_id}", users.eve), 404, code="NOT_FOUND")


@pytest.mark.us("US11")
def test_member_can_read_campaign(api, users, world):
    """Member can read the campaign"""
    api.check(api.get(f"/campaigns/{world.campaign_id}", users.bob), 200, my_role="creator", name="Spring Launch")


@pytest.mark.us("US11")
def test_campaign_creator_is_inserted_as_owner_member(api, users, world):
    """Member list contains the owner and all added members with one role each"""
    body = api.check(api.get(f"/campaigns/{world.campaign_id}/members", users.alice), 200,
                     **{"0.member_role": "owner", "0.email": "alice@example.com"})
    api.verify("campaign has 5 members (owner + 4 added)", len(body), 5, api="GET /api/v1/campaigns/{campaign_id}/members")


@pytest.mark.us("US11")
def test_non_member_cannot_list_members(api, users, world):
    """Outsider cannot list members"""
    api.check(api.get(f"/campaigns/{world.campaign_id}/members", users.eve), 404, code="NOT_FOUND")


@pytest.mark.us("US11", "US6")
def test_owner_adds_member(api, users, world):
    """Owner adds a registered user as reviewer"""
    api.get("/me", users.eve)
    r = api.post(f"/campaigns/{world.campaign_id}/members", users.alice,
                 json={"email": "EVE@example.com", "member_role": "reviewer"})
    api.check(r, 201, member_role="reviewer", email="eve@example.com", name="Eve Outsider")


@pytest.mark.us("US11")
def test_creator_cannot_add_member(api, users, world):
    """Only owners can add members"""
    api.get("/me", users.eve)
    r = api.post(f"/campaigns/{world.campaign_id}/members", users.bob,
                 json={"email": users.eve.email, "member_role": "reviewer"})
    api.check(r, 403, code="FORBIDDEN")


@pytest.mark.us("US11")
def test_add_unknown_email_fails(api, users, world):
    """Adding an email that never signed in returns 404 USER_NOT_FOUND"""
    r = api.post(f"/campaigns/{world.campaign_id}/members", users.alice,
                 json={"email": "ghost@example.com", "member_role": "creator"})
    api.check(r, 404, code="USER_NOT_FOUND")


@pytest.mark.us("US11")
def test_add_duplicate_member_fails(api, users, world):
    """A user has only one role per campaign"""
    r = api.post(f"/campaigns/{world.campaign_id}/members", users.alice,
                 json={"email": users.bob.email, "member_role": "reviewer"})
    api.check(r, 409, code="ALREADY_MEMBER")


@pytest.mark.us("US11")
def test_add_member_with_invalid_role_fails(api, users, world):
    """Only the four campaign roles are accepted"""
    api.get("/me", users.eve)
    r = api.post(f"/campaigns/{world.campaign_id}/members", users.alice,
                 json={"email": users.eve.email, "member_role": "admin"})
    api.check(r, 422, code="VALIDATION_ERROR", errors__0__field="member_role")


@pytest.mark.us("US11")
def test_add_member_with_invalid_email_fails(api, users, world):
    """Invalid email address is rejected"""
    r = api.post(f"/campaigns/{world.campaign_id}/members", users.alice,
                 json={"email": "not-an-email", "member_role": "creator"})
    api.check(r, 422, code="VALIDATION_ERROR", errors__0__field="email")


@pytest.mark.us("US11")
def test_last_owner_cannot_be_removed(api, users, world):
    """A campaign always keeps at least one owner"""
    api.check(api.delete(f"/campaigns/{world.campaign_id}/members/{users.alice.id}", users.alice),
              409, code="LAST_OWNER")


@pytest.mark.us("US11")
def test_removed_member_loses_access(api, users, world):
    """Removing a member revokes access immediately"""
    api.check(api.delete(f"/campaigns/{world.campaign_id}/members/{users.bob.id}", users.alice), 204)
    api.check(api.get(f"/campaigns/{world.campaign_id}", users.bob), 404, code="NOT_FOUND")


@pytest.mark.us("US11")
def test_only_owner_can_remove_member(api, users, world):
    """Creator cannot remove members"""
    api.check(api.delete(f"/campaigns/{world.campaign_id}/members/{users.carol.id}", users.bob),
              403, code="FORBIDDEN")


@pytest.mark.us("US11")
def test_remove_unknown_member_returns_404(api, users, world):
    """Removing a user who is not a member returns 404"""
    api.check(api.delete(f"/campaigns/{world.campaign_id}/members/{uuid.uuid4()}", users.alice), 404, code="NOT_FOUND")


@pytest.mark.us("US11")
def test_remove_member_with_malformed_id_returns_404(api, users, world):
    """Malformed member id returns 404, not a server error"""
    api.check(api.delete(f"/campaigns/{world.campaign_id}/members/not-a-uuid", users.alice), 404, code="NOT_FOUND")


@pytest.mark.us("US11")
def test_non_numeric_campaign_id_rejected(api, users):
    """Non-numeric path id is a validation error"""
    api.check(api.get("/campaigns/abc", users.alice), 422, code="VALIDATION_ERROR")
