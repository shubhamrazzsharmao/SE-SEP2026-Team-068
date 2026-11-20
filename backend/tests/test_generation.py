import pytest

from tests.helpers import PRESENT, Contains


@pytest.mark.us("US3")
def test_generate_creates_one_pending_piece_per_platform(api, users, brief):
    """One brief generates a pending-review piece for every selected platform"""
    body = api.check(api.post(f"/briefs/{brief.id}/generate", users.bob), 201,
                     job__status="done", job__error_message=None,
                     **{"pieces.0.platform": "blog", "pieces.0.status": "pending_review",
                        "pieces.0.current_version.version_no": 1,
                        "pieces.0.current_version.origin": "ai_generated",
                        "pieces.3.platform": "instagram"})
    api.verify("four pieces created", len(body["pieces"]), 4, api="POST /api/v1/briefs/{brief_id}/generate")


@pytest.mark.us("US3")
def test_instagram_piece_has_creative_suggestion(api, users, generated):
    """Instagram content comes with a creative suggestion"""
    api.check(api.get(f"/content/{generated.instagram}", users.carol), 200,
              current_version__creative_suggestion=PRESENT, platform="instagram")


@pytest.mark.us("US3", "US5")
def test_generated_content_uses_brand_terms(api, users, generated):
    """Generation is fed the brand's preferred terms"""
    api.check(api.get(f"/content/{generated.blog}", users.carol), 200,
              current_version__body=Contains("organic"))


@pytest.mark.us("US3", "US1")
def test_only_selected_platforms_are_generated(api, users, world):
    """Only the platforms in the brief are generated"""
    bid = api.post(f"/campaigns/{world.campaign_id}/briefs", users.bob,
                   json={"topic": "T", "objective": "O", "platforms": ["facebook"]}).json()["id"]
    body = api.check(api.post(f"/briefs/{bid}/generate", users.bob), 201, **{"pieces.0.platform": "facebook"})
    api.verify("exactly one piece", len(body["pieces"]), 1, api="POST /api/v1/briefs/{brief_id}/generate")


@pytest.mark.us("US3", "US6")
def test_nothing_is_approved_automatically(api, users, generated):
    """After generation nothing is approved: all four pieces await review"""
    api.check(api.get("/dashboard", users.alice), 200, totals__pending_review=4, totals__approved=0,
              totals__rejected=0)


@pytest.mark.us("US3")
def test_generate_twice_is_rejected(api, users, generated):
    """A brief can only be generated once"""
    api.check(api.post(f"/briefs/{generated.brief_id}/generate", users.bob), 409, code="BRIEF_ALREADY_GENERATED")


@pytest.mark.us("US3")
def test_reviewer_cannot_generate(api, users, brief):
    """Reviewers cannot trigger generation"""
    api.check(api.post(f"/briefs/{brief.id}/generate", users.carol), 403, code="FORBIDDEN")


@pytest.mark.us("US3")
def test_outsider_cannot_generate(api, users, brief):
    """Outsider gets 404 for the brief"""
    api.check(api.post(f"/briefs/{brief.id}/generate", users.eve), 404, code="NOT_FOUND")


@pytest.mark.us("US3")
def test_generate_unknown_brief(api, users, world):
    """Generating an unknown brief returns 404"""
    api.check(api.post("/briefs/9999/generate", users.alice), 404, code="NOT_FOUND")


@pytest.mark.us("US3")
def test_failed_generation_saves_nothing_and_can_be_retried(api, users, brief, failing_llm):
    """AI failure returns 502, saves no piece, keeps the brief editable and allows a retry"""
    failing_llm.on()
    api.check(api.post(f"/briefs/{brief.id}/generate", users.bob), 502, code="GENERATION_FAILED", job_id=PRESENT)
    api.check(api.get(f"/campaigns/{brief.campaign_id}/content", users.bob), 200, whole=[])
    api.check(api.get(f"/briefs/{brief.id}", users.bob), 200, status="draft")
    failing_llm.off()
    api.check(api.post(f"/briefs/{brief.id}/generate", users.bob), 201, job__status="done")


@pytest.mark.us("US3", "US13")
def test_failed_generation_is_logged(api, users, brief, failing_llm):
    """The failed attempt is recorded in the campaign activity log"""
    failing_llm.on()
    api.post(f"/briefs/{brief.id}/generate", users.bob)
    log = api.get(f"/campaigns/{brief.campaign_id}/activity", users.alice).json()
    api.verify("log contains generation_failed", "generation_failed" in [e["action"] for e in log], True,
               api="GET /api/v1/campaigns/{campaign_id}/activity")
