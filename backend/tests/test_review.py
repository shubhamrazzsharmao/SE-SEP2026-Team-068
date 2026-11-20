import pytest

from tests.helpers import PRESENT, Contains


# ---------------------------------------------------------------- US6: pending list
@pytest.mark.us("US6")
def test_reviewer_lists_pending_pieces(api, users, generated):
    """Reviewer lists the pieces pending review in a campaign"""
    body = api.check(api.get(f"/campaigns/{generated.campaign_id}/content", users.carol,
                             params={"status": "pending_review"}), 200, **{"0.status": "pending_review"})
    api.verify("four pending pieces", len(body), 4, api="GET /api/v1/campaigns/{campaign_id}/content")


# ---------------------------------------------------------------- US7: approve
@pytest.mark.us("US7")
def test_reviewer_approves_piece(api, users, generated):
    """Reviewer approves a pending piece"""
    api.check(api.post(f"/content/{generated.blog}/approve", users.carol), 200, status="approved")
    api.check(api.get(f"/content/{generated.blog}", users.carol), 200,
              reviews__0__decision="approved", reviews__0__reviewer_id=str(users.carol.id),
              reviews__0__created_at=PRESENT, reviews__0__version_no=1)


@pytest.mark.us("US7")
def test_creator_cannot_approve(api, users, generated):
    """A non-reviewer (creator) trying to approve gets 403"""
    api.check(api.post(f"/content/{generated.blog}/approve", users.bob), 403, code="FORBIDDEN")


@pytest.mark.us("US7")
def test_owner_cannot_approve(api, users, generated):
    """The campaign owner has no review rights (reviewer role only)"""
    api.check(api.post(f"/content/{generated.blog}/approve", users.alice), 403, code="FORBIDDEN")


@pytest.mark.us("US7")
def test_outsider_cannot_approve(api, users, generated):
    """Outsider gets 404 and cannot approve"""
    api.check(api.post(f"/content/{generated.blog}/approve", users.eve), 404, code="NOT_FOUND")


@pytest.mark.us("US7")
def test_cannot_approve_twice(api, users, generated):
    """Approving an already approved piece is a conflict"""
    api.post(f"/content/{generated.blog}/approve", users.carol)
    api.check(api.post(f"/content/{generated.blog}/approve", users.frank), 409, code="INVALID_STATE")


@pytest.mark.us("US7")
def test_reviewer_cannot_approve_own_edit(api, users, generated):
    """A reviewer cannot approve a version they wrote themselves"""
    api.patch(f"/content/{generated.blog}", users.carol, json={"body": "Carol's rewrite of the blog"})
    api.check(api.post(f"/content/{generated.blog}/approve", users.carol), 403, code="SELF_REVIEW_FORBIDDEN")
    api.check(api.post(f"/content/{generated.blog}/approve", users.frank), 200, status="approved")


@pytest.mark.us("US7")
def test_approval_of_stale_version_is_rejected(api, users, generated):
    """Approving version 1 after it was superseded by version 2 is refused"""
    api.patch(f"/content/{generated.blog}", users.bob, json={"body": "A newer draft"})
    r = api.post(f"/content/{generated.blog}/approve", users.carol, json={"version_no": 1})
    api.check(r, 409, code="STALE_VERSION")


@pytest.mark.us("US7")
def test_approval_of_current_version_succeeds(api, users, generated):
    """Approving with the right version_no works"""
    api.check(api.post(f"/content/{generated.blog}/approve", users.carol, json={"version_no": 1}), 200,
              status="approved")


@pytest.mark.us("US7")
def test_approve_unknown_piece(api, users, world):
    """Approving an unknown piece returns 404"""
    api.check(api.post("/content/9999/approve", users.carol), 404, code="NOT_FOUND")


# ---------------------------------------------------------------- US8: reject
@pytest.mark.us("US8")
def test_reject_with_reason(api, users, generated):
    """Reviewer rejects a piece with a reason; the creator can read it"""
    reason = "Claims about odour are not supported by the source."
    api.check(api.post(f"/content/{generated.linkedin}/reject", users.carol, json={"reason": reason}), 200,
              status="rejected", rejection_reason=reason)
    api.check(api.get(f"/content/{generated.linkedin}", users.bob), 200, status="rejected", rejection_reason=reason)


@pytest.mark.us("US8")
def test_reject_requires_reason(api, users, generated):
    """Rejection without a reason is refused"""
    api.check(api.post(f"/content/{generated.linkedin}/reject", users.carol, json={}), 422,
              code="VALIDATION_ERROR", errors__0__field="reason")


@pytest.mark.us("US8")
def test_reject_reason_must_be_ten_characters(api, users, generated):
    """A reason shorter than 10 characters is refused"""
    api.check(api.post(f"/content/{generated.linkedin}/reject", users.carol, json={"reason": "too short"}), 422,
              code="VALIDATION_ERROR", errors__0__field="reason")


@pytest.mark.us("US8")
def test_creator_cannot_reject(api, users, generated):
    """Creators cannot reject"""
    api.check(api.post(f"/content/{generated.linkedin}/reject", users.bob,
                       json={"reason": "I do not like this one."}), 403, code="FORBIDDEN")


@pytest.mark.us("US8")
def test_rejection_is_final_for_approve(api, users, generated):
    """A rejected piece cannot be approved afterwards"""
    api.post(f"/content/{generated.linkedin}/reject", users.carol, json={"reason": "Off-brand wording used."})
    api.check(api.post(f"/content/{generated.linkedin}/approve", users.frank), 409, code="INVALID_STATE",
              detail="Rejected content is final.")


@pytest.mark.us("US8")
def test_rejection_is_final_for_edit(api, users, generated):
    """A rejected piece cannot be edited"""
    api.post(f"/content/{generated.linkedin}/reject", users.carol, json={"reason": "Off-brand wording used."})
    api.check(api.patch(f"/content/{generated.linkedin}", users.bob, json={"body": "fixed"}), 409,
              code="INVALID_STATE")


@pytest.mark.us("US8")
def test_rejection_is_final_for_request_changes(api, users, generated):
    """A rejected piece cannot be regenerated"""
    api.post(f"/content/{generated.linkedin}/reject", users.carol, json={"reason": "Off-brand wording used."})
    api.check(api.post(f"/content/{generated.linkedin}/request-changes", users.frank,
                       json={"feedback": "try again please"}), 409, code="INVALID_STATE")


@pytest.mark.us("US8")
def test_rejected_piece_stays_in_history(api, users, generated):
    """Rejected content is kept, with its version and review"""
    api.post(f"/content/{generated.linkedin}/reject", users.carol, json={"reason": "Off-brand wording used."})
    api.check(api.get(f"/content/{generated.linkedin}", users.bob), 200, versions__0__version_no=1,
              reviews__0__decision="rejected")


# ---------------------------------------------------------------- US9: request changes
@pytest.mark.us("US9")
def test_request_changes_creates_one_new_version(api, users, generated):
    """Request changes yields one revised version and returns the piece to pending review"""
    r = api.post(f"/content/{generated.facebook}/request-changes", users.carol,
                 json={"feedback": "Make the call to action stronger."})
    api.check(r, 200, status="pending_review", current_version__version_no=2,
              current_version__origin="regeneration", current_version__body=Contains("stronger"))


@pytest.mark.us("US9")
def test_request_changes_keeps_old_version_and_logs_feedback(api, users, generated):
    """Version 1 and the feedback review are kept"""
    api.post(f"/content/{generated.facebook}/request-changes", users.carol,
             json={"feedback": "Make the call to action stronger."})
    body = api.check(api.get(f"/content/{generated.facebook}", users.bob), 200, versions__0__version_no=1,
                     versions__1__version_no=2, reviews__0__decision="changes_requested",
                     reviews__0__feedback="Make the call to action stronger.")
    api.verify("two versions exist", len(body["versions"]), 2, api="GET /api/v1/content/{piece_id}")


@pytest.mark.us("US9")
def test_request_changes_only_touches_that_piece(api, users, generated):
    """Other pieces of the same brief stay on version 1"""
    api.post(f"/content/{generated.facebook}/request-changes", users.carol, json={"feedback": "Stronger CTA please."})
    api.check(api.get(f"/content/{generated.blog}", users.carol), 200, current_version__version_no=1,
              status="pending_review")


@pytest.mark.us("US9")
def test_request_changes_requires_feedback(api, users, generated):
    """Request changes without feedback is refused"""
    api.check(api.post(f"/content/{generated.facebook}/request-changes", users.carol, json={}), 422,
              code="VALIDATION_ERROR", errors__0__field="feedback")


@pytest.mark.us("US9")
def test_creator_cannot_request_changes(api, users, generated):
    """Creators cannot request changes (reviewer action)"""
    api.check(api.post(f"/content/{generated.facebook}/request-changes", users.bob,
                       json={"feedback": "Make it shorter please"}), 403, code="FORBIDDEN")


@pytest.mark.us("US9")
def test_request_changes_failure_saves_nothing(api, users, generated, failing_llm):
    """AI failure on regeneration returns 502 and leaves the piece untouched"""
    failing_llm.on()
    api.check(api.post(f"/content/{generated.facebook}/request-changes", users.carol,
                       json={"feedback": "Make the call to action stronger."}), 502, code="GENERATION_FAILED")
    failing_llm.off()
    api.check(api.get(f"/content/{generated.facebook}", users.carol), 200, status="pending_review",
              current_version__version_no=1, reviews=[])


@pytest.mark.us("US9")
def test_request_changes_stale_version(api, users, generated):
    """Feedback on an outdated version is refused"""
    api.patch(f"/content/{generated.facebook}", users.bob, json={"body": "Newer text"})
    api.check(api.post(f"/content/{generated.facebook}/request-changes", users.carol,
                       json={"feedback": "Stronger CTA please.", "version_no": 1}), 409, code="STALE_VERSION")


@pytest.mark.us("US9", "US7")
def test_full_cycle_request_changes_then_approve(api, users, generated):
    """Request changes, then approve the revised version"""
    api.post(f"/content/{generated.facebook}/request-changes", users.carol, json={"feedback": "Stronger CTA please."})
    api.check(api.post(f"/content/{generated.facebook}/approve", users.carol, json={"version_no": 2}), 200,
              status="approved", current_version__version_no=2)
