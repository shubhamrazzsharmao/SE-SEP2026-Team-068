import pytest

from tests.helpers import PRESENT, Contains

BRAND = {"name": "Acme Tea", "tone": "friendly and calm", "preferred_terms": ["handpicked"],
         "avoided_terms": ["cheap"]}


@pytest.mark.us("US5")
def test_create_brand(api, users):
    """Create a brand with tone, preferred and avoided terms"""
    api.get("/me", users.alice)
    api.check(api.post("/brands", users.alice, json=BRAND), 201, name="Acme Tea",
              tone="friendly and calm", preferred_terms=["handpicked"], avoided_terms=["cheap"],
              owner_id=str(users.alice.id))


@pytest.mark.us("US5")
def test_create_brand_requires_tone(api, users):
    """Brand without tone is rejected"""
    r = api.post("/brands", users.alice, json={"name": "No Tone"})
    api.check(r, 422, code="VALIDATION_ERROR", errors__0__field="tone")


@pytest.mark.us("US5")
def test_create_brand_blank_name_rejected(api, users):
    """Brand with a whitespace-only name is rejected"""
    r = api.post("/brands", users.alice, json={"name": "   ", "tone": "calm"})
    api.check(r, 422, code="VALIDATION_ERROR", errors__0__field="name")


@pytest.mark.us("US5")
def test_duplicate_brand_name_rejected(api, users):
    """Same owner cannot create two brands with one name"""
    api.post("/brands", users.alice, json=BRAND)
    api.check(api.post("/brands", users.alice, json=BRAND), 409, code="DUPLICATE")


@pytest.mark.us("US5")
def test_terms_are_trimmed_and_deduplicated(api, users):
    """Blank and repeated terms are dropped from the term lists"""
    r = api.post("/brands", users.alice, json={**BRAND, "preferred_terms": [" organic ", "", "organic", "local"]})
    api.check(r, 201, preferred_terms=["organic", "local"])


@pytest.mark.us("US5", "US11")
def test_list_brands_only_shows_accessible_ones(api, users, world):
    """Owner and campaign members see the brand; an outsider sees none"""
    api.check(api.get("/brands", users.bob), 200, **{"0.name": "GreenLeaf Organics"})
    api.check(api.get("/brands", users.eve), 200, whole=[])


@pytest.mark.us("US5")
def test_outsider_cannot_read_brand(api, users, world):
    """Outsider gets 404 for someone else's brand"""
    api.check(api.get(f"/brands/{world.brand_id}", users.eve), 404, code="NOT_FOUND")


@pytest.mark.us("US5")
def test_member_can_read_brand(api, users, world):
    """Campaign member can read the brand guidelines"""
    api.check(api.get(f"/brands/{world.brand_id}", users.carol), 200, name="GreenLeaf Organics")


@pytest.mark.us("US5")
def test_brand_manager_can_update_tone(api, users, world):
    """Brand manager of a campaign can edit the brand tone"""
    r = api.patch(f"/brands/{world.brand_id}", users.dave, json={"tone": "bold and playful"})
    api.check(r, 200, tone="bold and playful", updated_by=str(users.dave.id))


@pytest.mark.us("US5")
def test_creator_cannot_update_brand(api, users, world):
    """Creator cannot edit brand guidelines"""
    api.check(api.patch(f"/brands/{world.brand_id}", users.bob, json={"tone": "x"}), 403, code="FORBIDDEN")


@pytest.mark.us("US5")
def test_outsider_cannot_update_brand(api, users, world):
    """Outsider cannot even see the brand to edit it"""
    api.check(api.patch(f"/brands/{world.brand_id}", users.eve, json={"tone": "x"}), 404, code="NOT_FOUND")


@pytest.mark.us("US5")
def test_empty_brand_update_rejected(api, users, world):
    """PATCH with an empty body is rejected"""
    api.check(api.patch(f"/brands/{world.brand_id}", users.alice, json={}), 422, code="VALIDATION_ERROR")


@pytest.mark.us("US5")
def test_rename_to_existing_brand_rejected(api, users, world):
    """Renaming a brand to another brand's name (same owner) is rejected"""
    api.post("/brands", users.alice, json=BRAND)
    r = api.patch(f"/brands/{world.brand_id}", users.alice, json={"name": "Acme Tea"})
    api.check(r, 409, code="DUPLICATE")


@pytest.mark.us("US5", "US3")
def test_brand_change_does_not_alter_existing_content(api, users, generated):
    """Brand changes apply only to content generated afterwards"""
    before = api.get(f"/content/{generated.blog}", users.carol).json()["current_version"]["body"]
    api.patch(f"/brands/{api.get(f'/campaigns/{generated.campaign_id}', users.alice).json()['brand_id']}",
              users.alice, json={"tone": "completely different tone", "preferred_terms": ["zzz"]})
    api.check(api.get(f"/content/{generated.blog}", users.carol), 200, current_version__body=before,
              current_version__version_no=1)
