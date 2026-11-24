import pytest

from tests.helpers import BRIEF


@pytest.mark.us("US1")
def test_create_brief_uses_brand_tone(api, users, world):
    """Creator submits a brief; the brand tone is used by default"""
    r = api.post(f"/campaigns/{world.campaign_id}/briefs", users.bob, json=BRIEF)
    api.check(r, 201, topic="Spring Compost Kit", status="draft", tone=None,
              effective_tone="warm, practical, no jargon", platforms=["blog", "linkedin", "facebook", "instagram"],
              created_by=str(users.bob.id))


@pytest.mark.us("US1")
def test_brief_tone_overrides_brand_tone(api, users, world):
    """A brief can override the brand tone for itself only"""
    r = api.post(f"/campaigns/{world.campaign_id}/briefs", users.bob, json={**BRIEF, "tone": "urgent"})
    api.check(r, 201, tone="urgent", effective_tone="urgent")


@pytest.mark.us("US1")
def test_optional_fields_may_be_omitted(api, users, world):
    """Audience and key messages are optional"""
    r = api.post(f"/campaigns/{world.campaign_id}/briefs", users.alice,
                 json={"topic": "T", "objective": "O", "platforms": ["blog"]})
    api.check(r, 201, target_audience=None, key_messages=None)


@pytest.mark.us("US1")
def test_duplicate_platforms_are_collapsed(api, users, world):
    """Repeated platforms are stored once"""
    r = api.post(f"/campaigns/{world.campaign_id}/briefs", users.bob,
                 json={**BRIEF, "platforms": ["blog", "blog", "facebook"]})
    api.check(r, 201, platforms=["blog", "facebook"])


@pytest.mark.us("US1")
def test_brief_requires_topic(api, users, world):
    """Brief without a topic is rejected"""
    body = {k: v for k, v in BRIEF.items() if k != "topic"}
    api.check(api.post(f"/campaigns/{world.campaign_id}/briefs", users.bob, json=body), 422,
              code="VALIDATION_ERROR", errors__0__field="topic")


@pytest.mark.us("US1")
def test_brief_requires_a_platform(api, users, world):
    """Brief with an empty platform list is rejected"""
    api.check(api.post(f"/campaigns/{world.campaign_id}/briefs", users.bob, json={**BRIEF, "platforms": []}),
              422, code="VALIDATION_ERROR", errors__0__field="platforms")


@pytest.mark.us("US1")
def test_brief_rejects_unknown_platform(api, users, world):
    """Only blog, linkedin, facebook and instagram are accepted"""
    api.check(api.post(f"/campaigns/{world.campaign_id}/briefs", users.bob, json={**BRIEF, "platforms": ["twitter"]}),
              422, code="VALIDATION_ERROR")


@pytest.mark.us("US1")
def test_brief_blank_objective_rejected(api, users, world):
    """A whitespace-only objective is rejected"""
    api.check(api.post(f"/campaigns/{world.campaign_id}/briefs", users.bob, json={**BRIEF, "objective": "  "}),
              422, code="VALIDATION_ERROR", errors__0__field="objective")


@pytest.mark.us("US1")
def test_reviewer_cannot_create_brief(api, users, world):
    """Reviewers cannot create briefs"""
    api.check(api.post(f"/campaigns/{world.campaign_id}/briefs", users.carol, json=BRIEF), 403, code="FORBIDDEN")


@pytest.mark.us("US1")
def test_brand_manager_cannot_create_brief(api, users, world):
    """Brand managers cannot create briefs"""
    api.check(api.post(f"/campaigns/{world.campaign_id}/briefs", users.dave, json=BRIEF), 403, code="FORBIDDEN")


@pytest.mark.us("US1", "US11")
def test_outsider_cannot_create_brief(api, users, world):
    """Outsider gets 404 for the campaign"""
    api.check(api.post(f"/campaigns/{world.campaign_id}/briefs", users.eve, json=BRIEF), 404, code="NOT_FOUND")


@pytest.mark.us("US1")
def test_edit_draft_brief(api, users, brief):
    """A saved brief can be edited until generation starts"""
    r = api.patch(f"/briefs/{brief.id}", users.bob, json={"topic": "New Topic", "platforms": ["blog"]})
    api.check(r, 200, topic="New Topic", platforms=["blog"], status="draft")


@pytest.mark.us("US1")
def test_empty_brief_update_rejected(api, users, brief):
    """PATCH with no fields is rejected"""
    api.check(api.patch(f"/briefs/{brief.id}", users.bob, json={}), 422, code="VALIDATION_ERROR")


@pytest.mark.us("US1")
def test_null_required_brief_field_rejected(api, users, brief):
    """A required field cannot be set to null"""
    api.check(api.patch(f"/briefs/{brief.id}", users.bob, json={"topic": None}), 422, code="VALIDATION_ERROR")


@pytest.mark.us("US1")
def test_brief_locked_after_generation(api, users, generated):
    """Briefs cannot be edited once generation has run"""
    api.check(api.patch(f"/briefs/{generated.brief_id}", users.bob, json={"topic": "Too late"}),
              409, code="BRIEF_LOCKED")


@pytest.mark.us("US1")
def test_reviewer_cannot_edit_brief(api, users, brief):
    """Reviewers cannot edit briefs"""
    api.check(api.patch(f"/briefs/{brief.id}", users.carol, json={"topic": "x"}), 403, code="FORBIDDEN")


@pytest.mark.us("US6")
def test_reviewer_can_read_brief(api, users, brief):
    """Reviewer can read the brief next to the content"""
    api.check(api.get(f"/briefs/{brief.id}", users.carol), 200, topic="Spring Compost Kit")


@pytest.mark.us("US1")
def test_outsider_cannot_read_brief(api, users, brief):
    """Outsider gets 404 for a brief"""
    api.check(api.get(f"/briefs/{brief.id}", users.eve), 404, code="NOT_FOUND")


@pytest.mark.us("US1", "US11")
def test_list_briefs_of_campaign(api, users, brief):
    """Members list the briefs of a campaign"""
    api.check(api.get(f"/campaigns/{brief.campaign_id}/briefs", users.carol), 200, **{"0.id": brief.id})


@pytest.mark.us("US1")
def test_unknown_brief_returns_404(api, users, world):
    """Unknown brief id returns 404"""
    api.check(api.get("/briefs/9999", users.alice), 404, code="NOT_FOUND")
