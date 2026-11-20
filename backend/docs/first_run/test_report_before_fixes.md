# ContentFlow API - test report

Cases recorded: **160**  |  Passed: **155**  |  Failed: **5**

Each case lists the request that was sent, what we expected and what the API actually returned.

## Cases where actual output differed from expected

- **TC-093** PATCH /api/v1/content/{piece_id} - An edit is saved as a new human_edit version
- **TC-094** PATCH /api/v1/content/{piece_id} - Editing an approved piece sends it back to pending review
- **TC-095** PATCH /api/v1/content/{piece_id} - Edit with an empty body is refused
- **TC-108** POST /api/v1/content/{piece_id}/comments - Blank comment is refused
- **TC-151** POST /api/v1/content/{piece_id}/request-changes - Request changes yields one revised version and returns the piece to pending review

## All cases

### TC-001 - The piece log lists generation, edit and approval with user, action and version  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/activity`  |  **User story:** US13
- **Input:** as Dave BrandManager (dave); path /api/v1/content/1/activity
- **Expected:** HTTP 200; 0.action = "generated"; 0.user_name = "Bob Creator"; 0.version_no = 1; 1.action = "edited"; 1.version_no = 2; 1.user_name = "Bob Creator"; 2.action = "approved"; 2.user_name = "Carol Reviewer"; 2.version_no = 2; 2.created_at = <present>
- **Actual:** HTTP 200 [{"id": 8, "campaign_id": 1, "piece_id": 1, "user_id": "f7fd66b6-5826-4244-ae55-64e462adc168", "user_name": "Bob Creator", "action": "generated", "version_no": 1, "detail": {"platform": "blog", "job_id": 1}, "created_at": "2026-11-20T17:14:00.353334"}, {"id": 12, "campaign_id": 1, "piece_id": 1, "user_id": "f7fd66b6-5826-4244-ae55-64e462adc168", "user_name": "Bob Creator", "action": "edited", "version_no": 2, "detail ...(truncated)

### TC-002 - Change-request notes and regenerations are logged  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/activity`  |  **User story:** US13, US9
- **Input:** as Bob Creator (bob); path /api/v1/content/3/activity
- **Expected:** HTTP 200; 1.action = "changes_requested"; 1.detail.feedback = "Stronger CTA please."; 1.version_no = 1; 2.action = "regenerated"; 2.version_no = 2
- **Actual:** HTTP 200 [{"id": 10, "campaign_id": 1, "piece_id": 3, "user_id": "3c482d6f-8a96-4bbf-b01e-f81aa7824b66", "user_name": "Bob Creator", "action": "generated", "version_no": 1, "detail": {"platform": "facebook", "job_id": 1}, "created_at": "2026-11-20T17:14:00.678009"}, {"id": 12, "campaign_id": 1, "piece_id": 3, "user_id": "2285ebe1-2839-423e-ac4c-0bb72224e78e", "user_name": "Carol Reviewer", "action": "changes_requested", "vers ...(truncated)

### TC-003 - The rejection and its reason are logged  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/activity`  |  **User story:** US13, US8
- **Input:** as Bob Creator (bob); path /api/v1/content/1/activity
- **Expected:** HTTP 200; 1.action = "rejected"; 1.detail.reason = "Not suitable for our audience."
- **Actual:** HTTP 200 [{"id": 8, "campaign_id": 1, "piece_id": 1, "user_id": "08f644b2-1eba-4428-9426-80b36faf41e2", "user_name": "Bob Creator", "action": "generated", "version_no": 1, "detail": {"platform": "blog", "job_id": 1}, "created_at": "2026-11-20T17:14:00.854367"}, {"id": 12, "campaign_id": 1, "piece_id": 1, "user_id": "13ff4d1f-0740-4568-b50c-cff1403f500c", "user_name": "Carol Reviewer", "action": "rejected", "version_no": 1, "d ...(truncated)

### TC-004 - Outsider gets 404 for a piece's log  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/activity`  |  **User story:** US13
- **Input:** as Eve Outsider (eve); path /api/v1/content/1/activity
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-005 - Owner sees the campaign log, newest first  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/activity`  |  **User story:** US13
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/activity
- **Expected:** HTTP 200; 0.action = "approved"; 0.user_name = "Carol Reviewer"
- **Actual:** HTTP 200 [{"id": 12, "campaign_id": 1, "piece_id": 1, "user_id": "1da2f17b-d9d7-4202-957a-6bae87a77f63", "user_name": "Carol Reviewer", "action": "approved", "version_no": 1, "detail": null, "created_at": "2026-11-20T17:14:01.138957"}, {"id": 11, "campaign_id": 1, "piece_id": 4, "user_id": "be0f3b50-d61a-43f2-9fda-93c26750d0bf", "user_name": "Bob Creator", "action": "generated", "version_no": 1, "detail": {"platform": "instag ...(truncated)

### TC-006 - Creators cannot read the campaign-wide log  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/activity`  |  **User story:** US13
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/activity
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: owner.", "code": "FORBIDDEN"}

### TC-007 - A global admin can read any campaign's log  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/activity`  |  **User story:** US13
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns/1/activity
- **Expected:** HTTP 200; 0.action = <present>
- **Actual:** HTTP 200 [{"id": 11, "campaign_id": 1, "piece_id": 4, "user_id": "ed2c97e6-e6ef-4267-a359-3ee64e92b044", "user_name": "Bob Creator", "action": "generated", "version_no": 1, "detail": {"platform": "instagram", "job_id": 1}, "created_at": "2026-11-20T17:14:01.480332"}, {"id": 10, "campaign_id": 1, "piece_id": 3, "user_id": "ed2c97e6-e6ef-4267-a359-3ee64e92b044", "user_name": "Bob Creator", "action": "generated", "version_no": 1 ...(truncated)

### TC-008 - Admin asking for a campaign that does not exist gets 404  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/activity`  |  **User story:** US13
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns/9999/activity
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Campaign not found.", "code": "NOT_FOUND"}

### TC-009 - There is no way to modify or delete log entries  `PASS`
- **API:** `DELETE /api/v1/content/1/activity`  |  **User story:** US13
- **Input:** as Alice Owner (alice); path /api/v1/content/1/activity
- **Expected:** HTTP 405; code = "METHOD_NOT_ALLOWED"
- **Actual:** HTTP 405 {"detail": "Method Not Allowed", "code": "METHOD_NOT_ALLOWED"}

### TC-010 - There is no way to modify or delete log entries  `PASS`
- **API:** `POST /api/v1/content/1/activity`  |  **User story:** US13
- **Input:** as Alice Owner (alice); path /api/v1/content/1/activity; body {"action": "x"}
- **Expected:** HTTP 405; code = "METHOD_NOT_ALLOWED"
- **Actual:** HTTP 405 {"detail": "Method Not Allowed", "code": "METHOD_NOT_ALLOWED"}

### TC-011 - Request without a bearer token is rejected  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as no token; path /api/v1/me
- **Expected:** HTTP 401; code = "UNAUTHORIZED"; detail = "Missing bearer token."
- **Actual:** HTTP 401 {"detail": "Missing bearer token.", "code": "UNAUTHORIZED"}

### TC-012 - Malformed token is rejected  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as custom token; path /api/v1/me
- **Expected:** HTTP 401; code = "UNAUTHORIZED"; detail = "Invalid token."
- **Actual:** HTTP 401 {"detail": "Invalid token.", "code": "UNAUTHORIZED"}

### TC-013 - Expired token is rejected  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as custom token; path /api/v1/me
- **Expected:** HTTP 401; code = "UNAUTHORIZED"; detail = "Token has expired."
- **Actual:** HTTP 401 {"detail": "Token has expired.", "code": "UNAUTHORIZED"}

### TC-014 - Token signed with a different secret (forged) is rejected  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as custom token; path /api/v1/me
- **Expected:** HTTP 401; code = "UNAUTHORIZED"; detail = "Invalid token."
- **Actual:** HTTP 401 {"detail": "Invalid token.", "code": "UNAUTHORIZED"}

### TC-015 - Token for a different audience is rejected  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as custom token; path /api/v1/me
- **Expected:** HTTP 401; code = "UNAUTHORIZED"
- **Actual:** HTTP 401 {"detail": "Invalid token.", "code": "UNAUTHORIZED"}

### TC-016 - Unsigned token (alg=none) is rejected  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as custom token; path /api/v1/me
- **Expected:** HTTP 401; code = "UNAUTHORIZED"; detail = "Token algorithm not accepted."
- **Actual:** HTTP 401 {"detail": "Token algorithm not accepted.", "code": "UNAUTHORIZED"}

### TC-017 - First authenticated call creates the profile from the token claims  `PASS`
- **API:** `GET /api/v1/me`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/me
- **Expected:** HTTP 200; name = "Alice Owner"; email = "alice@example.com"; role = "user"; id = "c78d2a00-dd30-4d6e-b0f2-4543b5b3cc07"
- **Actual:** HTTP 200 {"id": "c78d2a00-dd30-4d6e-b0f2-4543b5b3cc07", "name": "Alice Owner", "email": "alice@example.com", "role": "user"}

### TC-018 - Name falls back to the email prefix when the token has no name  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as custom token; path /api/v1/me
- **Expected:** HTTP 200; name = "bob"; email = "bob@example.com"
- **Actual:** HTTP 200 {"id": "b3f79cc7-9b3b-48f1-abd4-992ebf35764b", "name": "bob", "email": "bob@example.com", "role": "user"}

### TC-019 - Token of an unknown user without an email claim is rejected  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as custom token; path /api/v1/me
- **Expected:** HTTP 401; code = "UNAUTHORIZED"; detail = "Token has no email claim."
- **Actual:** HTTP 401 {"detail": "Token has no email claim.", "code": "UNAUTHORIZED"}

### TC-020 - Disabled account gets 403  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as Alice Owner (alice); path /api/v1/me
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This account is disabled.", "code": "FORBIDDEN"}

### TC-021 - Health check works without a token and reports the database  `PASS`
- **API:** `GET /api/v1/health`
- **Input:** as no token; path /api/v1/health
- **Expected:** HTTP 200; status = "ok"; database = true
- **Actual:** HTTP 200 {"status": "ok", "database": true}

### TC-022 - Unknown URL returns the standard error body  `PASS`
- **API:** `GET /api/v1/nope`
- **Input:** as Alice Owner (alice); path /api/v1/nope
- **Expected:** HTTP 404; code = "NOT_FOUND"; detail = <present>
- **Actual:** HTTP 404 {"detail": "Not Found", "code": "NOT_FOUND"}

### TC-023 - Wrong HTTP method returns 405 in the standard error body  `PASS`
- **API:** `PUT /api/v1/me`
- **Input:** as Alice Owner (alice); path /api/v1/me
- **Expected:** HTTP 405; code = "METHOD_NOT_ALLOWED"
- **Actual:** HTTP 405 {"detail": "Method Not Allowed", "code": "METHOD_NOT_ALLOWED"}

### TC-024 - Create a brand with tone, preferred and avoided terms  `PASS`
- **API:** `POST /api/v1/brands`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands; body {"name": "Acme Tea", "tone": "friendly and calm", "preferred_terms": ["handpicked"], "avoided_terms": ["cheap"]}
- **Expected:** HTTP 201; name = "Acme Tea"; tone = "friendly and calm"; preferred_terms = ["handpicked"]; avoided_terms = ["cheap"]; owner_id = "5a79d0cb-1b61-4510-9132-29c897113693"
- **Actual:** HTTP 201 {"id": 1, "owner_id": "5a79d0cb-1b61-4510-9132-29c897113693", "name": "Acme Tea", "tone": "friendly and calm", "preferred_terms": ["handpicked"], "avoided_terms": ["cheap"], "updated_by": "5a79d0cb-1b61-4510-9132-29c897113693", "created_at": "2026-11-20T17:14:02.326270Z", "updated_at": "2026-11-20T17:14:02.326274Z"}

### TC-025 - Brand without tone is rejected  `PASS`
- **API:** `POST /api/v1/brands`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands; body {"name": "No Tone"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "tone"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "tone", "message": "Field required"}]}

### TC-026 - Brand with a whitespace-only name is rejected  `PASS`
- **API:** `POST /api/v1/brands`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands; body {"name": "   ", "tone": "calm"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "name"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "name", "message": "String should have at least 1 character"}]}

### TC-027 - Same owner cannot create two brands with one name  `PASS`
- **API:** `POST /api/v1/brands`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands; body {"name": "Acme Tea", "tone": "friendly and calm", "preferred_terms": ["handpicked"], "avoided_terms": ["cheap"]}
- **Expected:** HTTP 409; code = "DUPLICATE"
- **Actual:** HTTP 409 {"detail": "You already have a brand with this name.", "code": "DUPLICATE"}

### TC-028 - Blank and repeated terms are dropped from the term lists  `PASS`
- **API:** `POST /api/v1/brands`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands; body {"name": "Acme Tea", "tone": "friendly and calm", "preferred_terms": [" organic ", "", "organic", "local"], "avoided_terms": ["cheap"]}
- **Expected:** HTTP 201; preferred_terms = ["organic", "local"]
- **Actual:** HTTP 201 {"id": 1, "owner_id": "3cc3e4ac-a592-41e6-a644-7bb5007cf498", "name": "Acme Tea", "tone": "friendly and calm", "preferred_terms": ["organic", "local"], "avoided_terms": ["cheap"], "updated_by": "3cc3e4ac-a592-41e6-a644-7bb5007cf498", "created_at": "2026-11-20T17:14:02.516286Z", "updated_at": "2026-11-20T17:14:02.516290Z"}

### TC-029 - Owner and campaign members see the brand; an outsider sees none  `PASS`
- **API:** `GET /api/v1/brands`  |  **User story:** US5, US11
- **Input:** as Bob Creator (bob); path /api/v1/brands
- **Expected:** HTTP 200; 0.name = "GreenLeaf Organics"
- **Actual:** HTTP 200 [{"id": 1, "owner_id": "de2a302f-25b6-4d6a-a62a-f3eb37ceaa2d", "name": "GreenLeaf Organics", "tone": "warm, practical, no jargon", "preferred_terms": ["organic", "sustainable"], "avoided_terms": ["cheap", "chemical"], "updated_by": "de2a302f-25b6-4d6a-a62a-f3eb37ceaa2d", "created_at": "2026-11-20T17:14:02.599296", "updated_at": "2026-11-20T17:14:02.599299"}]

### TC-030 - Owner and campaign members see the brand; an outsider sees none  `PASS`
- **API:** `GET /api/v1/brands`  |  **User story:** US5, US11
- **Input:** as Eve Outsider (eve); path /api/v1/brands
- **Expected:** HTTP 200; response body == []
- **Actual:** HTTP 200 []

### TC-031 - Outsider gets 404 for someone else's brand  `PASS`
- **API:** `GET /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Eve Outsider (eve); path /api/v1/brands/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brand not found.", "code": "NOT_FOUND"}

### TC-032 - Campaign member can read the brand guidelines  `PASS`
- **API:** `GET /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Carol Reviewer (carol); path /api/v1/brands/1
- **Expected:** HTTP 200; name = "GreenLeaf Organics"
- **Actual:** HTTP 200 {"id": 1, "owner_id": "6c1051e8-5fce-4c40-9438-4e57c4d55cfa", "name": "GreenLeaf Organics", "tone": "warm, practical, no jargon", "preferred_terms": ["organic", "sustainable"], "avoided_terms": ["cheap", "chemical"], "updated_by": "6c1051e8-5fce-4c40-9438-4e57c4d55cfa", "created_at": "2026-11-20T17:14:02.821977", "updated_at": "2026-11-20T17:14:02.821982"}

### TC-033 - Brand manager of a campaign can edit the brand tone  `PASS`
- **API:** `PATCH /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Dave BrandManager (dave); path /api/v1/brands/1; body {"tone": "bold and playful"}
- **Expected:** HTTP 200; tone = "bold and playful"; updated_by = "6d758e54-0a38-4348-9448-b2c6d590718c"
- **Actual:** HTTP 200 {"id": 1, "owner_id": "8ffae905-d726-4f1e-8a2d-9753cba96650", "name": "GreenLeaf Organics", "tone": "bold and playful", "preferred_terms": ["organic", "sustainable"], "avoided_terms": ["cheap", "chemical"], "updated_by": "6d758e54-0a38-4348-9448-b2c6d590718c", "created_at": "2026-11-20T17:14:02.928346", "updated_at": "2026-11-20T17:14:02.969284Z"}

### TC-034 - Creator cannot edit brand guidelines  `PASS`
- **API:** `PATCH /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Bob Creator (bob); path /api/v1/brands/1; body {"tone": "x"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "Only the brand owner or a brand manager can edit a brand.", "code": "FORBIDDEN"}

### TC-035 - Outsider cannot even see the brand to edit it  `PASS`
- **API:** `PATCH /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Eve Outsider (eve); path /api/v1/brands/1; body {"tone": "x"}
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brand not found.", "code": "NOT_FOUND"}

### TC-036 - PATCH with an empty body is rejected  `PASS`
- **API:** `PATCH /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands/1; body {}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "", "message": "Value error, Provide at least one field to update."}]}

### TC-037 - Renaming a brand to another brand's name (same owner) is rejected  `PASS`
- **API:** `PATCH /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands/1; body {"name": "Acme Tea"}
- **Expected:** HTTP 409; code = "DUPLICATE"
- **Actual:** HTTP 409 {"detail": "A brand with this name already exists.", "code": "DUPLICATE"}

### TC-038 - Brand changes apply only to content generated afterwards  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US5, US3
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1
- **Expected:** HTTP 200; current_version.body = "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from recycled material\n\n## What to do next\nTone: warm, practical, no jargon. Key terms: organic, sustainable.\n\n## Conclusion\nDrive pre-orders of the compost kit"; current_version.version_no = 1
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "f3667a84-577a-4751-bfff-b726f48db401", "created_at": "2026-11-20T17:14:03.612707", "updated_at": "2026-11-20T17:14:03.613529", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made  ...(truncated)

### TC-039 - Creator submits a brief; the brand tone is used by default  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 201; topic = "Spring Compost Kit"; status = "draft"; tone = null; effective_tone = "warm, practical, no jargon"; platforms = ["blog", "linkedin", "facebook", "instagram"]; created_by = "3baf73a6-ef3b-4f28-93f1-630e14ff778c"
- **Actual:** HTTP 201 {"id": 1, "campaign_id": 1, "created_by": "3baf73a6-ef3b-4f28-93f1-630e14ff778c", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog", "linkedin", "facebook", "instagram"], "status": "draft", "created_at ...(truncated)

### TC-040 - A brief can override the brand tone for itself only  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"], "tone": "urgent"}
- **Expected:** HTTP 201; tone = "urgent"; effective_tone = "urgent"
- **Actual:** HTTP 201 {"id": 1, "campaign_id": 1, "created_by": "bafe1da9-b1b1-45df-aa4e-f6f1d211b475", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": "urgent", "effective_tone": "urgent", "platforms": ["blog", "linkedin", "facebook", "instagram"], "status": "draft", "created_at": "2026-11-20T1 ...(truncated)

### TC-041 - Audience and key messages are optional  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/briefs; body {"topic": "T", "objective": "O", "platforms": ["blog"]}
- **Expected:** HTTP 201; target_audience = null; key_messages = null
- **Actual:** HTTP 201 {"id": 1, "campaign_id": 1, "created_by": "e5dbe021-4abc-4950-ad6e-0100c5bb9b6a", "topic": "T", "objective": "O", "target_audience": null, "key_messages": null, "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog"], "status": "draft", "created_at": "2026-11-20T17:14:03.992765Z", "updated_at": "2026-11-20T17:14:03.992768Z"}

### TC-042 - Repeated platforms are stored once  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "blog", "facebook"]}
- **Expected:** HTTP 201; platforms = ["blog", "facebook"]
- **Actual:** HTTP 201 {"id": 1, "campaign_id": 1, "created_by": "71a50927-c5b9-4a7e-b3e9-793523d21431", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog", "facebook"], "status": "draft", "created_at": "2026-11-20T17:14:04.1 ...(truncated)

### TC-043 - Brief without a topic is rejected  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "topic"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "topic", "message": "Field required"}]}

### TC-044 - Brief with an empty platform list is rejected  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": []}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "platforms"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "platforms", "message": "List should have at least 1 item after validation, not 0"}]}

### TC-045 - Only blog, linkedin, facebook and instagram are accepted  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["twitter"]}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "platforms.0", "message": "Input should be 'blog', 'linkedin', 'facebook' or 'instagram'"}]}

### TC-046 - A whitespace-only objective is rejected  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "  ", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "objective"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "objective", "message": "String should have at least 1 character"}]}

### TC-047 - Reviewers cannot create briefs  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Carol Reviewer (carol); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner.", "code": "FORBIDDEN"}

### TC-048 - Brand managers cannot create briefs  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Dave BrandManager (dave); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner.", "code": "FORBIDDEN"}

### TC-049 - Outsider gets 404 for the campaign  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1, US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Campaign not found.", "code": "NOT_FOUND"}

### TC-050 - A saved brief can be edited until generation starts  `PASS`
- **API:** `PATCH /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1; body {"topic": "New Topic", "platforms": ["blog"]}
- **Expected:** HTTP 200; topic = "New Topic"; platforms = ["blog"]; status = "draft"
- **Actual:** HTTP 200 {"id": 1, "campaign_id": 1, "created_by": "d6066ddc-fce8-482f-915d-612e1b1ad632", "topic": "New Topic", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog"], "status": "draft", "created_at": "2026-11-20T17:14:05.090281", "updated_at": ...(truncated)

### TC-051 - PATCH with no fields is rejected  `PASS`
- **API:** `PATCH /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1; body {}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "", "message": "Value error, Provide at least one field to update."}]}

### TC-052 - A required field cannot be set to null  `PASS`
- **API:** `PATCH /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1; body {"topic": null}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "", "message": "Value error, topic cannot be null."}]}

### TC-053 - Briefs cannot be edited once generation has run  `PASS`
- **API:** `PATCH /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1; body {"topic": "Too late"}
- **Expected:** HTTP 409; code = "BRIEF_LOCKED"
- **Actual:** HTTP 409 {"detail": "The brief can no longer be edited because generation has started.", "code": "BRIEF_LOCKED"}

### TC-054 - Reviewers cannot edit briefs  `PASS`
- **API:** `PATCH /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Carol Reviewer (carol); path /api/v1/briefs/1; body {"topic": "x"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner.", "code": "FORBIDDEN"}

### TC-055 - Reviewer can read the brief next to the content  `PASS`
- **API:** `GET /api/v1/briefs/{brief_id}`  |  **User story:** US6
- **Input:** as Carol Reviewer (carol); path /api/v1/briefs/1
- **Expected:** HTTP 200; topic = "Spring Compost Kit"
- **Actual:** HTTP 200 {"id": 1, "campaign_id": 1, "created_by": "2bae3e31-fccf-4acd-821c-6b5283bb0c5b", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog", "linkedin", "facebook", "instagram"], "status": "draft", "created_at ...(truncated)

### TC-056 - Outsider gets 404 for a brief  `PASS`
- **API:** `GET /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Eve Outsider (eve); path /api/v1/briefs/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brief not found.", "code": "NOT_FOUND"}

### TC-057 - Members list the briefs of a campaign  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1, US11
- **Input:** as Carol Reviewer (carol); path /api/v1/campaigns/1/briefs
- **Expected:** HTTP 200; 0.id = 1
- **Actual:** HTTP 200 [{"id": 1, "campaign_id": 1, "created_by": "3a759595-6b04-4074-9e72-4f16fc85b0a6", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog", "linkedin", "facebook", "instagram"], "status": "draft", "created_a ...(truncated)

### TC-058 - Unknown brief id returns 404  `PASS`
- **API:** `GET /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Alice Owner (alice); path /api/v1/briefs/9999
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brief not found.", "code": "NOT_FOUND"}

### TC-059 - Create a campaign under an own brand; the creator becomes owner  `PASS`
- **API:** `POST /api/v1/campaigns`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns; body {"brand_id": 1, "name": "Autumn Sale"}
- **Expected:** HTTP 201; name = "Autumn Sale"; my_role = "owner"; brand_name = "GreenLeaf Organics"
- **Actual:** HTTP 201 {"id": 2, "brand_id": 1, "brand_name": "GreenLeaf Organics", "name": "Autumn Sale", "description": null, "created_at": "2026-11-20T17:14:06.419987Z", "my_role": "owner"}

### TC-060 - Cannot create a campaign on somebody else's brand  `PASS`
- **API:** `POST /api/v1/campaigns`  |  **User story:** US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns; body {"brand_id": 1, "name": "Hijack"}
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brand not found.", "code": "NOT_FOUND"}

### TC-061 - Campaign without a name is rejected  `PASS`
- **API:** `POST /api/v1/campaigns`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns; body {"brand_id": 1}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "name"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "name", "message": "Field required"}]}

### TC-062 - Members list their campaign with their role; outsiders see nothing  `PASS`
- **API:** `GET /api/v1/campaigns`  |  **User story:** US11
- **Input:** as Carol Reviewer (carol); path /api/v1/campaigns
- **Expected:** HTTP 200; 0.my_role = "reviewer"; 0.id = 1
- **Actual:** HTTP 200 [{"id": 1, "brand_id": 1, "brand_name": "GreenLeaf Organics", "name": "Spring Launch", "description": "Spring product launch", "created_at": "2026-11-20T17:14:06.765792", "my_role": "reviewer"}]

### TC-063 - Members list their campaign with their role; outsiders see nothing  `PASS`
- **API:** `GET /api/v1/campaigns`  |  **User story:** US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns
- **Expected:** HTTP 200; response body == []
- **Actual:** HTTP 200 []

### TC-064 - Non-member cannot see that a campaign exists  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}`  |  **User story:** US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Campaign not found.", "code": "NOT_FOUND"}

### TC-065 - Member can read the campaign  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1
- **Expected:** HTTP 200; my_role = "creator"; name = "Spring Launch"
- **Actual:** HTTP 200 {"id": 1, "brand_id": 1, "brand_name": "GreenLeaf Organics", "name": "Spring Launch", "description": "Spring product launch", "created_at": "2026-11-20T17:14:07.036759", "my_role": "creator"}

### TC-066 - Member list contains the owner and all added members with one role each  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members
- **Expected:** HTTP 200; 0.member_role = "owner"; 0.email = "alice@example.com"
- **Actual:** HTTP 200 [{"user_id": "08fbaf34-3c5e-466d-9bcd-46d81dd58980", "name": "Alice Owner", "email": "alice@example.com", "member_role": "owner", "joined_at": "2026-11-20T17:14:07.154425"}, {"user_id": "7972471c-1a5c-404a-ac9e-8db806c525c7", "name": "Bob Creator", "email": "bob@example.com", "member_role": "creator", "joined_at": "2026-11-20T17:14:07.161460"}, {"user_id": "34f70db5-c9d5-48ce-a4d1-d563c52eba4f", "name": "Carol Review ...(truncated)

### TC-067 - campaign has 5 members (owner + 4 added)  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/members`
- **Input:** -
- **Expected:** 5
- **Actual:** 5

### TC-068 - Outsider cannot list members  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns/1/members
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Campaign not found.", "code": "NOT_FOUND"}

### TC-069 - Owner adds a registered user as reviewer  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11, US6
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members; body {"email": "EVE@example.com", "member_role": "reviewer"}
- **Expected:** HTTP 201; member_role = "reviewer"; email = "eve@example.com"; name = "Eve Outsider"
- **Actual:** HTTP 201 {"user_id": "18e76fda-58c1-4eb4-807a-080fac8e8096", "name": "Eve Outsider", "email": "eve@example.com", "member_role": "reviewer", "joined_at": "2026-11-20T17:14:07.419816Z"}

### TC-070 - Only owners can add members  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/members; body {"email": "eve@example.com", "member_role": "reviewer"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: owner.", "code": "FORBIDDEN"}

### TC-071 - Adding an email that never signed in returns 404 USER_NOT_FOUND  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members; body {"email": "ghost@example.com", "member_role": "creator"}
- **Expected:** HTTP 404; code = "USER_NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "No user with that email. Ask them to sign in to the app once first.", "code": "USER_NOT_FOUND"}

### TC-072 - A user has only one role per campaign  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members; body {"email": "bob@example.com", "member_role": "reviewer"}
- **Expected:** HTTP 409; code = "ALREADY_MEMBER"
- **Actual:** HTTP 409 {"detail": "That user is already a member of this campaign.", "code": "ALREADY_MEMBER"}

### TC-073 - Only the four campaign roles are accepted  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members; body {"email": "eve@example.com", "member_role": "admin"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "member_role"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "member_role", "message": "Input should be 'owner', 'creator', 'reviewer' or 'brand_manager'"}]}

### TC-074 - Invalid email address is rejected  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members; body {"email": "not-an-email", "member_role": "creator"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "email"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "email", "message": "Value error, Not a valid email address."}]}

### TC-075 - A campaign always keeps at least one owner  `PASS`
- **API:** `DELETE /api/v1/campaigns/{campaign_id}/members/{user_id}`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members/256a1883-d693-4ee3-aff6-a91063ca1ef3
- **Expected:** HTTP 409; code = "LAST_OWNER"
- **Actual:** HTTP 409 {"detail": "A campaign must keep at least one owner.", "code": "LAST_OWNER"}

### TC-076 - Removing a member revokes access immediately  `PASS`
- **API:** `DELETE /api/v1/campaigns/{campaign_id}/members/{user_id}`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members/98344d7e-375c-499a-a8fe-9301f19b6974
- **Expected:** HTTP 204
- **Actual:** HTTP 204

### TC-077 - Removing a member revokes access immediately  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Campaign not found.", "code": "NOT_FOUND"}

### TC-078 - Creator cannot remove members  `PASS`
- **API:** `DELETE /api/v1/campaigns/{campaign_id}/members/{user_id}`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/members/5426670a-2010-4e17-acd4-e0bae648c6cf
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: owner.", "code": "FORBIDDEN"}

### TC-079 - Removing a user who is not a member returns 404  `PASS`
- **API:** `DELETE /api/v1/campaigns/{campaign_id}/members/{user_id}`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members/167a6572-5697-4a15-aba0-3ad6d6e17e6a
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Member not found.", "code": "NOT_FOUND"}

### TC-080 - Malformed member id returns 404, not a server error  `PASS`
- **API:** `DELETE /api/v1/campaigns/{campaign_id}/members/{user_id}`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members/not-a-uuid
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Member not found.", "code": "NOT_FOUND"}

### TC-081 - Non-numeric path id is a validation error  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/abc
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "path.campaign_id", "message": "Input should be a valid integer, unable to parse string as an integer"}]}

### TC-082 - Filter a campaign's content by status  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US10
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/content; query {"status": "approved"}
- **Expected:** HTTP 200; 0.platform = "blog"
- **Actual:** HTTP 200 [{"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "approved", "created_by": "eb9a5726-1816-49e8-a496-1b98d6324434", "created_at": "2026-11-20T17:14:08.814095", "updated_at": "2026-11-20T17:14:08.831122", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from  ...(truncated)

### TC-083 - one approved piece  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`
- **Input:** -
- **Expected:** 1
- **Actual:** 1

### TC-084 - Filter a campaign's content by status  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US10
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/content; query {"status": "rejected"}
- **Expected:** HTTP 200; 0.platform = "linkedin"; 0.rejection_reason = "Wording is off-brand."
- **Actual:** HTTP 200 [{"id": 2, "brief_id": 1, "campaign_id": 1, "platform": "linkedin", "status": "rejected", "created_by": "eb9a5726-1816-49e8-a496-1b98d6324434", "created_at": "2026-11-20T17:14:08.815770", "updated_at": "2026-11-20T17:14:08.841563", "current_version": {"id": 2, "version_no": 1, "body": "Spring Compost Kit: what urban gardeners should know.\n\nEasy, odour-free, made from recycled material\n\nKey terms: organic, sustain ...(truncated)

### TC-085 - two pending pieces  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`
- **Input:** -
- **Expected:** 2
- **Actual:** 2

### TC-086 - Filter a campaign's content by platform  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US10
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/content; query {"platform": "instagram"}
- **Expected:** HTTP 200; 0.platform = "instagram"
- **Actual:** HTTP 200 [{"id": 4, "brief_id": 1, "campaign_id": 1, "platform": "instagram", "status": "pending_review", "created_by": "326eb705-9c74-4558-bbf9-239782f6a3ac", "created_at": "2026-11-20T17:14:09.001558", "updated_at": "2026-11-20T17:14:09.002665", "current_version": {"id": 4, "version_no": 1, "body": "Spring Compost Kit | Easy, odour-free, made from recycled material\n\n#spring #brand #campaign", "creative_suggestion": "Brigh ...(truncated)

### TC-087 - one instagram piece  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`
- **Input:** -
- **Expected:** 1
- **Actual:** 1

### TC-088 - Unknown status value is a validation error  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US10
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/content; query {"status": "published"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "query.status", "message": "Input should be 'draft', 'pending_review', 'approved' or 'rejected'"}]}

### TC-089 - Outsider gets 404 when listing a campaign's content  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US10, US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns/1/content
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Campaign not found.", "code": "NOT_FOUND"}

### TC-090 - Reviewer opens a piece next to its brief  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US6
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1
- **Expected:** HTTP 200; brief.topic = "Spring Compost Kit"; brief.key_messages = <present>; versions.0.version_no = 1; current_version.version_no = 1
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "b592bf19-9dfb-4e9c-a36b-85fca66981be", "created_at": "2026-11-20T17:14:09.440076", "updated_at": "2026-11-20T17:14:09.441929", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made  ...(truncated)

### TC-091 - Outsider gets 404 for a piece  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US6
- **Input:** as Eve Outsider (eve); path /api/v1/content/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-092 - Versions come back oldest first  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/versions`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/versions
- **Expected:** HTTP 200; 0.version_no = 1; 0.origin = "ai_generated"; 1.version_no = 2; 1.origin = "human_edit"
- **Actual:** HTTP 200 [{"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from recycled material\n\n## What to do next\nTone: warm, practical, no jargon. Key terms: organic, sustainable.\n\n## Conclusion\nDrive pre-orders of the compost kit", "creative_suggestion": null, "origin": "ai_generated", "model_name": "fake-llm-v1" ...(truncated)

### TC-093 - An edit is saved as a new human_edit version  `FAIL`
- **API:** `PATCH /api/v1/content/{piece_id}`  |  **User story:** US6, US13
- **Input:** as Bob Creator (bob); path /api/v1/content/1; body {"body": "My improved blog text"}
- **Expected:** HTTP 200; status = "pending_review"; current_version.version_no = 2; current_version.origin = "human_edit"; current_version.body = "My improved blog text"; current_version.created_by = "9985f6aa-9dd9-4552-8a10-3d167b1db9a7"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "9985f6aa-9dd9-4552-8a10-3d167b1db9a7", "created_at": "2026-11-20T17:14:09.944461", "updated_at": "2026-11-20T17:14:09.958236Z", "current_version": null, "rejection_reason": null}

### TC-094 - Editing an approved piece sends it back to pending review  `FAIL`
- **API:** `PATCH /api/v1/content/{piece_id}`  |  **User story:** US6
- **Input:** as Bob Creator (bob); path /api/v1/content/1; body {"body": "Changed after approval"}
- **Expected:** HTTP 200; status = "pending_review"; current_version.version_no = 2
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "04b60121-bf4a-4193-ba9b-53b226f678b4", "created_at": "2026-11-20T17:14:10.117924", "updated_at": "2026-11-20T17:14:10.143438Z", "current_version": null, "rejection_reason": null}

### TC-095 - Edit with an empty body is refused  `FAIL`
- **API:** `PATCH /api/v1/content/{piece_id}`  |  **User story:** US6
- **Input:** as Bob Creator (bob); path /api/v1/content/1; body {"body": "  "}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "body"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "", "message": "String should have at least 1 character"}]}

### TC-096 - Brand managers cannot edit content  `PASS`
- **API:** `PATCH /api/v1/content/{piece_id}`  |  **User story:** US6
- **Input:** as Dave BrandManager (dave); path /api/v1/content/1; body {"body": "x"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner, reviewer.", "code": "FORBIDDEN"}

### TC-097 - Deleting without the confirmation flag is refused  `PASS`
- **API:** `DELETE /api/v1/content/{piece_id}`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/content/1
- **Expected:** HTTP 400; code = "CONFIRMATION_REQUIRED"
- **Actual:** HTTP 400 {"detail": "Deleting content needs confirmation: repeat the request with ?confirm=true.", "code": "CONFIRMATION_REQUIRED"}

### TC-098 - Deleting without the confirmation flag is refused  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/content/1
- **Expected:** HTTP 200; status = "pending_review"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "630393b4-5354-4529-a617-1a818956c3f8", "created_at": "2026-11-20T17:14:10.620715", "updated_at": "2026-11-20T17:14:10.621743", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made  ...(truncated)

### TC-099 - Confirmed delete hides the piece; versions and log are kept  `PASS`
- **API:** `DELETE /api/v1/content/{piece_id}`  |  **User story:** US11, US13
- **Input:** as Bob Creator (bob); path /api/v1/content/1; query {"confirm": "true"}
- **Expected:** HTTP 204
- **Actual:** HTTP 204

### TC-100 - Confirmed delete hides the piece; versions and log are kept  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US11, US13
- **Input:** as Bob Creator (bob); path /api/v1/content/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-101 - deleted piece is not listed  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`
- **Input:** -
- **Expected:** false
- **Actual:** false

### TC-102 - version rows are kept  `PASS`
- **API:** `database check`
- **Input:** -
- **Expected:** 1
- **Actual:** 1

### TC-103 - deletion is logged  `PASS`
- **API:** `database check`
- **Input:** -
- **Expected:** 1
- **Actual:** 1

### TC-104 - Reviewers cannot delete content  `PASS`
- **API:** `DELETE /api/v1/content/{piece_id}`  |  **User story:** US11
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1; query {"confirm": "true"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner.", "code": "FORBIDDEN"}

### TC-105 - Any member can comment on a piece  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/comments`  |  **User story:** US6, US8
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/comments; body {"body": "Please cite the source."}
- **Expected:** HTTP 201; body = "Please cite the source."; author_name = "Carol Reviewer"; user_id = "21fd5566-c506-4358-aeef-73c56117e61e"
- **Actual:** HTTP 201 {"id": 1, "piece_id": 1, "user_id": "21fd5566-c506-4358-aeef-73c56117e61e", "author_name": "Carol Reviewer", "body": "Please cite the source.", "created_at": "2026-11-20T17:14:11.162060Z"}

### TC-106 - Any member can comment on a piece  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/comments`  |  **User story:** US6, US8
- **Input:** as Bob Creator (bob); path /api/v1/content/1/comments; body {"body": "Added in the next draft."}
- **Expected:** HTTP 201
- **Actual:** HTTP 201 {"id": 2, "piece_id": 1, "user_id": "30509125-c923-4cee-b036-d3cb9f982266", "author_name": "Bob Creator", "body": "Added in the next draft.", "created_at": "2026-11-20T17:14:11.168113Z"}

### TC-107 - Any member can comment on a piece  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/comments`  |  **User story:** US6, US8
- **Input:** as Dave BrandManager (dave); path /api/v1/content/1/comments
- **Expected:** HTTP 200; 0.author_name = "Carol Reviewer"; 1.author_name = "Bob Creator"
- **Actual:** HTTP 200 [{"id": 1, "piece_id": 1, "user_id": "21fd5566-c506-4358-aeef-73c56117e61e", "author_name": "Carol Reviewer", "body": "Please cite the source.", "created_at": "2026-11-20T17:14:11.162060"}, {"id": 2, "piece_id": 1, "user_id": "30509125-c923-4cee-b036-d3cb9f982266", "author_name": "Bob Creator", "body": "Added in the next draft.", "created_at": "2026-11-20T17:14:11.168113"}]

### TC-108 - Blank comment is refused  `FAIL`
- **API:** `POST /api/v1/content/{piece_id}/comments`  |  **User story:** US6
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/comments; body {"body": "   "}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "body"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "", "message": "String should have at least 1 character"}]}

### TC-109 - Outsider cannot comment or read comments  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/comments`  |  **User story:** US6
- **Input:** as Eve Outsider (eve); path /api/v1/content/1/comments; body {"body": "hi"}
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-110 - Outsider cannot comment or read comments  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/comments`  |  **User story:** US6
- **Input:** as Eve Outsider (eve); path /api/v1/content/1/comments
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-111 - Dashboard counts pieces per status, in total and per campaign  `PASS`
- **API:** `GET /api/v1/dashboard`  |  **User story:** US10
- **Input:** as Bob Creator (bob); path /api/v1/dashboard
- **Expected:** HTTP 200; totals.approved = 1; totals.rejected = 1; totals.pending_review = 2; campaigns.0.counts.approved = 1; campaigns.0.campaign_id = 1
- **Actual:** HTTP 200 {"totals": {"draft": 0, "pending_review": 2, "approved": 1, "rejected": 1}, "campaigns": [{"campaign_id": 1, "name": "Spring Launch", "counts": {"draft": 0, "pending_review": 2, "approved": 1, "rejected": 1}}]}

### TC-112 - A user without campaigns gets an empty dashboard  `PASS`
- **API:** `GET /api/v1/dashboard`  |  **User story:** US10
- **Input:** as Eve Outsider (eve); path /api/v1/dashboard
- **Expected:** HTTP 200; totals.pending_review = 0; campaigns = []
- **Actual:** HTTP 200 {"totals": {"draft": 0, "pending_review": 0, "approved": 0, "rejected": 0}, "campaigns": []}

### TC-113 - One brief generates a pending-review piece for every selected platform  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1/generate
- **Expected:** HTTP 201; job.status = "done"; job.error_message = null; pieces.0.platform = "blog"; pieces.0.status = "pending_review"; pieces.0.current_version.version_no = 1; pieces.0.current_version.origin = "ai_generated"; pieces.3.platform = "instagram"
- **Actual:** HTTP 201 {"job": {"id": 1, "brief_id": 1, "platform": null, "status": "done", "error_message": null, "feedback_note": null, "created_at": "2026-11-20T17:14:11.833248Z", "finished_at": "2026-11-20T17:14:11.838396Z"}, "pieces": [{"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "9b573f25-7f21-4f18-9401-a2be5b2f90c2", "created_at": "2026-11-20T17:14:11.835562Z", "updated_at" ...(truncated)

### TC-114 - four pieces created  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`
- **Input:** -
- **Expected:** 4
- **Actual:** 4

### TC-115 - Instagram content comes with a creative suggestion  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US3
- **Input:** as Carol Reviewer (carol); path /api/v1/content/4
- **Expected:** HTTP 200; current_version.creative_suggestion = <present>; platform = "instagram"
- **Actual:** HTTP 200 {"id": 4, "brief_id": 1, "campaign_id": 1, "platform": "instagram", "status": "pending_review", "created_by": "445e515a-d830-404b-8cf1-90ae0def0d9c", "created_at": "2026-11-20T17:14:11.984815", "updated_at": "2026-11-20T17:14:11.985587", "current_version": {"id": 4, "version_no": 1, "body": "Spring Compost Kit | Easy, odour-free, made from recycled material\n\n#spring #brand #campaign", "creative_suggestion": "Bright ...(truncated)

### TC-116 - Generation is fed the brand's preferred terms  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US3, US5
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1
- **Expected:** HTTP 200; current_version.body = contains 'organic'
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "5d4d536a-92ce-4e26-8a0d-f5df6e53fe60", "created_at": "2026-11-20T17:14:12.114190", "updated_at": "2026-11-20T17:14:12.115543", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made  ...(truncated)

### TC-117 - Only the platforms in the brief are generated  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3, US1
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1/generate
- **Expected:** HTTP 201; pieces.0.platform = "facebook"
- **Actual:** HTTP 201 {"job": {"id": 1, "brief_id": 1, "platform": null, "status": "done", "error_message": null, "feedback_note": null, "created_at": "2026-11-20T17:14:12.240561Z", "finished_at": "2026-11-20T17:14:12.244317Z"}, "pieces": [{"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "facebook", "status": "pending_review", "created_by": "bbea660a-ab74-4deb-9439-d540b161e84d", "created_at": "2026-11-20T17:14:12.243713Z", "updated ...(truncated)

### TC-118 - exactly one piece  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`
- **Input:** -
- **Expected:** 1
- **Actual:** 1

### TC-119 - After generation nothing is approved: all four pieces await review  `PASS`
- **API:** `GET /api/v1/dashboard`  |  **User story:** US3, US6
- **Input:** as Alice Owner (alice); path /api/v1/dashboard
- **Expected:** HTTP 200; totals.pending_review = 4; totals.approved = 0; totals.rejected = 0
- **Actual:** HTTP 200 {"totals": {"draft": 0, "pending_review": 4, "approved": 0, "rejected": 0}, "campaigns": [{"campaign_id": 1, "name": "Spring Launch", "counts": {"draft": 0, "pending_review": 4, "approved": 0, "rejected": 0}}]}

### TC-120 - A brief can only be generated once  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1/generate
- **Expected:** HTTP 409; code = "BRIEF_ALREADY_GENERATED"
- **Actual:** HTTP 409 {"detail": "Content was already generated for this brief (status: generated).", "code": "BRIEF_ALREADY_GENERATED"}

### TC-121 - Reviewers cannot trigger generation  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Carol Reviewer (carol); path /api/v1/briefs/1/generate
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner.", "code": "FORBIDDEN"}

### TC-122 - Outsider gets 404 for the brief  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Eve Outsider (eve); path /api/v1/briefs/1/generate
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brief not found.", "code": "NOT_FOUND"}

### TC-123 - Generating an unknown brief returns 404  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Alice Owner (alice); path /api/v1/briefs/9999/generate
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brief not found.", "code": "NOT_FOUND"}

### TC-124 - AI failure returns 502, saves no piece, keeps the brief editable and allows a retry  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1/generate
- **Expected:** HTTP 502; code = "GENERATION_FAILED"; job_id = <present>
- **Actual:** HTTP 502 {"detail": "The AI provider failed; nothing was saved. You can retry.", "code": "GENERATION_FAILED", "job_id": 1}

### TC-125 - AI failure returns 502, saves no piece, keeps the brief editable and allows a retry  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/content
- **Expected:** HTTP 200; response body == []
- **Actual:** HTTP 200 []

### TC-126 - AI failure returns 502, saves no piece, keeps the brief editable and allows a retry  `PASS`
- **API:** `GET /api/v1/briefs/{brief_id}`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1
- **Expected:** HTTP 200; status = "draft"
- **Actual:** HTTP 200 {"id": 1, "campaign_id": 1, "created_by": "ecccb37a-7af7-42eb-9a7e-ce2124198498", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog", "linkedin", "facebook", "instagram"], "status": "draft", "created_at ...(truncated)

### TC-127 - AI failure returns 502, saves no piece, keeps the brief editable and allows a retry  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1/generate
- **Expected:** HTTP 201; job.status = "done"
- **Actual:** HTTP 201 {"job": {"id": 2, "brief_id": 1, "platform": null, "status": "done", "error_message": null, "feedback_note": null, "created_at": "2026-11-20T17:14:13.077010Z", "finished_at": "2026-11-20T17:14:13.082726Z"}, "pieces": [{"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "ecccb37a-7af7-42eb-9a7e-ce2124198498", "created_at": "2026-11-20T17:14:13.079696Z", "updated_at" ...(truncated)

### TC-128 - log contains generation_failed  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/activity`
- **Input:** -
- **Expected:** true
- **Actual:** true

### TC-129 - Reviewer lists the pieces pending review in a campaign  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US6
- **Input:** as Carol Reviewer (carol); path /api/v1/campaigns/1/content; query {"status": "pending_review"}
- **Expected:** HTTP 200; 0.status = "pending_review"
- **Actual:** HTTP 200 [{"id": 4, "brief_id": 1, "campaign_id": 1, "platform": "instagram", "status": "pending_review", "created_by": "7f908b5c-7e54-49ed-b688-de0481eebbe8", "created_at": "2026-11-20T17:14:13.401077", "updated_at": "2026-11-20T17:14:13.401952", "current_version": {"id": 4, "version_no": 1, "body": "Spring Compost Kit | Easy, odour-free, made from recycled material\n\n#spring #brand #campaign", "creative_suggestion": "Brigh ...(truncated)

### TC-130 - four pending pieces  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`
- **Input:** -
- **Expected:** 4
- **Actual:** 4

### TC-131 - Reviewer approves a pending piece  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/approve
- **Expected:** HTTP 200; status = "approved"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "approved", "created_by": "54c1fdd8-21fa-400b-971c-0f0baa7cf348", "created_at": "2026-11-20T17:14:13.545945", "updated_at": "2026-11-20T17:14:13.564866Z", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from  ...(truncated)

### TC-132 - Reviewer approves a pending piece  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1
- **Expected:** HTTP 200; reviews.0.decision = "approved"; reviews.0.reviewer_id = "18268766-1e67-47c8-9a02-81a94bc00f25"; reviews.0.created_at = <present>; reviews.0.version_no = 1
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "approved", "created_by": "54c1fdd8-21fa-400b-971c-0f0baa7cf348", "created_at": "2026-11-20T17:14:13.545945", "updated_at": "2026-11-20T17:14:13.564866", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from r ...(truncated)

### TC-133 - A non-reviewer (creator) trying to approve gets 403  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Bob Creator (bob); path /api/v1/content/1/approve
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: reviewer.", "code": "FORBIDDEN"}

### TC-134 - The campaign owner has no review rights (reviewer role only)  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Alice Owner (alice); path /api/v1/content/1/approve
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: reviewer.", "code": "FORBIDDEN"}

### TC-135 - Outsider gets 404 and cannot approve  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Eve Outsider (eve); path /api/v1/content/1/approve
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-136 - Approving an already approved piece is a conflict  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Frank Reviewer (frank); path /api/v1/content/1/approve
- **Expected:** HTTP 409; code = "INVALID_STATE"
- **Actual:** HTTP 409 {"detail": "Only pieces in pending_review can be reviewed (current status: approved).", "code": "INVALID_STATE"}

### TC-137 - A reviewer cannot approve a version they wrote themselves  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/approve
- **Expected:** HTTP 403; code = "SELF_REVIEW_FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "You cannot review content you created or edited.", "code": "SELF_REVIEW_FORBIDDEN"}

### TC-138 - A reviewer cannot approve a version they wrote themselves  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Frank Reviewer (frank); path /api/v1/content/1/approve
- **Expected:** HTTP 200; status = "approved"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "approved", "created_by": "632bd30c-2f46-41f3-bafb-b1d5e8404174", "created_at": "2026-11-20T17:14:14.265008", "updated_at": "2026-11-20T17:14:14.293353Z", "current_version": {"id": 5, "version_no": 2, "body": "Carol's rewrite of the blog", "creative_suggestion": null, "origin": "human_edit", "model_name": null, "flags": null, "created_by": "e6d3 ...(truncated)

### TC-139 - Approving version 1 after it was superseded by version 2 is refused  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/approve; body {"version_no": 1}
- **Expected:** HTTP 409; code = "STALE_VERSION"
- **Actual:** HTTP 409 {"detail": "You reviewed version 1, but the current version is 2.", "code": "STALE_VERSION"}

### TC-140 - Approving with the right version_no works  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/approve; body {"version_no": 1}
- **Expected:** HTTP 200; status = "approved"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "approved", "created_by": "96da5249-487e-41b4-89c5-9d3fa16788be", "created_at": "2026-11-20T17:14:14.602479", "updated_at": "2026-11-20T17:14:14.616722Z", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from  ...(truncated)

### TC-141 - Approving an unknown piece returns 404  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/9999/approve
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-142 - Reviewer rejects a piece with a reason; the creator can read it  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/reject`  |  **User story:** US8
- **Input:** as Carol Reviewer (carol); path /api/v1/content/2/reject; body {"reason": "Claims about odour are not supported by the source."}
- **Expected:** HTTP 200; status = "rejected"; rejection_reason = "Claims about odour are not supported by the source."
- **Actual:** HTTP 200 {"id": 2, "brief_id": 1, "campaign_id": 1, "platform": "linkedin", "status": "rejected", "created_by": "a3205dc0-1619-4cc1-b90e-294bdafeb177", "created_at": "2026-11-20T17:14:14.857413", "updated_at": "2026-11-20T17:14:14.869445Z", "current_version": {"id": 2, "version_no": 1, "body": "Spring Compost Kit: what urban gardeners should know.\n\nEasy, odour-free, made from recycled material\n\nKey terms: organic, sustain ...(truncated)

### TC-143 - Reviewer rejects a piece with a reason; the creator can read it  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US8
- **Input:** as Bob Creator (bob); path /api/v1/content/2
- **Expected:** HTTP 200; status = "rejected"; rejection_reason = "Claims about odour are not supported by the source."
- **Actual:** HTTP 200 {"id": 2, "brief_id": 1, "campaign_id": 1, "platform": "linkedin", "status": "rejected", "created_by": "a3205dc0-1619-4cc1-b90e-294bdafeb177", "created_at": "2026-11-20T17:14:14.857413", "updated_at": "2026-11-20T17:14:14.869445", "current_version": {"id": 2, "version_no": 1, "body": "Spring Compost Kit: what urban gardeners should know.\n\nEasy, odour-free, made from recycled material\n\nKey terms: organic, sustaina ...(truncated)

### TC-144 - Rejection without a reason is refused  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/reject`  |  **User story:** US8
- **Input:** as Carol Reviewer (carol); path /api/v1/content/2/reject; body {}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "reason"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "reason", "message": "Field required"}]}

### TC-145 - A reason shorter than 10 characters is refused  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/reject`  |  **User story:** US8
- **Input:** as Carol Reviewer (carol); path /api/v1/content/2/reject; body {"reason": "too short"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "reason"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "reason", "message": "String should have at least 10 characters"}]}

### TC-146 - Creators cannot reject  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/reject`  |  **User story:** US8
- **Input:** as Bob Creator (bob); path /api/v1/content/2/reject; body {"reason": "I do not like this one."}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: reviewer.", "code": "FORBIDDEN"}

### TC-147 - A rejected piece cannot be approved afterwards  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US8
- **Input:** as Frank Reviewer (frank); path /api/v1/content/2/approve
- **Expected:** HTTP 409; code = "INVALID_STATE"; detail = "Rejected content is final."
- **Actual:** HTTP 409 {"detail": "Rejected content is final.", "code": "INVALID_STATE"}

### TC-148 - A rejected piece cannot be edited  `PASS`
- **API:** `PATCH /api/v1/content/{piece_id}`  |  **User story:** US8
- **Input:** as Bob Creator (bob); path /api/v1/content/2; body {"body": "fixed"}
- **Expected:** HTTP 409; code = "INVALID_STATE"
- **Actual:** HTTP 409 {"detail": "Rejected content is final and cannot be edited.", "code": "INVALID_STATE"}

### TC-149 - A rejected piece cannot be regenerated  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US8
- **Input:** as Frank Reviewer (frank); path /api/v1/content/2/request-changes; body {"feedback": "try again please"}
- **Expected:** HTTP 409; code = "INVALID_STATE"
- **Actual:** HTTP 409 {"detail": "Rejected content is final.", "code": "INVALID_STATE"}

### TC-150 - Rejected content is kept, with its version and review  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US8
- **Input:** as Bob Creator (bob); path /api/v1/content/2
- **Expected:** HTTP 200; versions.0.version_no = 1; reviews.0.decision = "rejected"
- **Actual:** HTTP 200 {"id": 2, "brief_id": 1, "campaign_id": 1, "platform": "linkedin", "status": "rejected", "created_by": "e82dfcf4-815b-4d99-9b4f-9357605a3b1b", "created_at": "2026-11-20T17:14:15.936527", "updated_at": "2026-11-20T17:14:15.949298", "current_version": {"id": 2, "version_no": 1, "body": "Spring Compost Kit: what urban gardeners should know.\n\nEasy, odour-free, made from recycled material\n\nKey terms: organic, sustaina ...(truncated)

### TC-151 - Request changes yields one revised version and returns the piece to pending review  `FAIL`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3/request-changes; body {"feedback": "Make the call to action stronger."}
- **Expected:** HTTP 200; status = "pending_review"; current_version.version_no = 2; current_version.origin = "regeneration"; current_version.body = contains 'stronger'
- **Actual:** HTTP 200 {"id": 3, "brief_id": 1, "campaign_id": 1, "platform": "facebook", "status": "pending_review", "created_by": "cb229281-bf78-4ae7-8d47-1df0a11fd8b6", "created_at": "2026-11-20T17:14:16.080482", "updated_at": "2026-11-20T17:14:16.093512Z", "current_version": null, "rejection_reason": null}

### TC-152 - Version 1 and the feedback review are kept  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US9
- **Input:** as Bob Creator (bob); path /api/v1/content/3
- **Expected:** HTTP 200; versions.0.version_no = 1; versions.1.version_no = 2; reviews.0.decision = "changes_requested"; reviews.0.feedback = "Make the call to action stronger."
- **Actual:** HTTP 200 {"id": 3, "brief_id": 1, "campaign_id": 1, "platform": "facebook", "status": "pending_review", "created_by": "7d1795e5-4b99-4943-8557-784996cea9a6", "created_at": "2026-11-20T17:14:16.238873", "updated_at": "2026-11-20T17:14:16.253629", "current_version": {"id": 5, "version_no": 2, "body": "Spring Compost Kit - Easy, odour-free, made from recycled material Key terms: organic, sustainable.\n\nLearn more today!\n\n[Rev ...(truncated)

### TC-153 - two versions exist  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`
- **Input:** -
- **Expected:** 2
- **Actual:** 2

### TC-154 - Other pieces of the same brief stay on version 1  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1
- **Expected:** HTTP 200; current_version.version_no = 1; status = "pending_review"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "40b2a42f-4bec-41d8-bfdc-019cad60e215", "created_at": "2026-11-20T17:14:16.389977", "updated_at": "2026-11-20T17:14:16.391274", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made  ...(truncated)

### TC-155 - Request changes without feedback is refused  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3/request-changes; body {}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "feedback"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "feedback", "message": "Field required"}]}

### TC-156 - Creators cannot request changes (reviewer action)  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US9
- **Input:** as Bob Creator (bob); path /api/v1/content/3/request-changes; body {"feedback": "Make it shorter please"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: reviewer.", "code": "FORBIDDEN"}

### TC-157 - AI failure on regeneration returns 502 and leaves the piece untouched  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3/request-changes; body {"feedback": "Make the call to action stronger."}
- **Expected:** HTTP 502; code = "GENERATION_FAILED"
- **Actual:** HTTP 502 {"detail": "The AI provider failed; no changes were saved. (simulated provider outage)", "code": "GENERATION_FAILED"}

### TC-158 - AI failure on regeneration returns 502 and leaves the piece untouched  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3
- **Expected:** HTTP 200; status = "pending_review"; current_version.version_no = 1; reviews = []
- **Actual:** HTTP 200 {"id": 3, "brief_id": 1, "campaign_id": 1, "platform": "facebook", "status": "pending_review", "created_by": "042a3782-4800-439a-9cc2-864b82043f8e", "created_at": "2026-11-20T17:14:16.873918", "updated_at": "2026-11-20T17:14:16.875304", "current_version": {"id": 3, "version_no": 1, "body": "Spring Compost Kit - Easy, odour-free, made from recycled material Key terms: organic, sustainable.\n\nLearn more today!", "crea ...(truncated)

### TC-159 - Feedback on an outdated version is refused  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3/request-changes; body {"feedback": "Stronger CTA please.", "version_no": 1}
- **Expected:** HTTP 409; code = "STALE_VERSION"
- **Actual:** HTTP 409 {"detail": "You reviewed version 1, but the current version is 2.", "code": "STALE_VERSION"}

### TC-160 - Request changes, then approve the revised version  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US9, US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3/approve; body {"version_no": 2}
- **Expected:** HTTP 200; status = "approved"; current_version.version_no = 2
- **Actual:** HTTP 200 {"id": 3, "brief_id": 1, "campaign_id": 1, "platform": "facebook", "status": "approved", "created_by": "dc691d11-c45f-4ae0-96a5-8a4291e6acb9", "created_at": "2026-11-20T17:14:17.180164", "updated_at": "2026-11-20T17:14:17.201786Z", "current_version": {"id": 5, "version_no": 2, "body": "Spring Compost Kit - Easy, odour-free, made from recycled material Key terms: organic, sustainable.\n\nLearn more today!\n\n[Revised  ...(truncated)
