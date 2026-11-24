# ContentFlow API - test report

Cases recorded: **162**  |  Passed: **162**  |  Failed: **0**

Each case lists the request that was sent, what we expected and what the API actually returned.

## All cases

### TC-001 - The piece log lists generation, edit and approval with user, action and version  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/activity`  |  **User story:** US13
- **Input:** as Dave BrandManager (dave); path /api/v1/content/1/activity
- **Expected:** HTTP 200; 0.action = "generated"; 0.user_name = "Bob Creator"; 0.version_no = 1; 1.action = "edited"; 1.version_no = 2; 1.user_name = "Bob Creator"; 2.action = "approved"; 2.user_name = "Carol Reviewer"; 2.version_no = 2; 2.created_at = <present>
- **Actual:** HTTP 200 [{"id": 8, "campaign_id": 1, "piece_id": 1, "user_id": "60942e38-5094-4f00-b5e6-6d4b3d0bc8af", "user_name": "Bob Creator", "action": "generated", "version_no": 1, "detail": {"platform": "blog", "job_id": 1}, "created_at": "2026-11-24T18:35:52.739533"}, {"id": 12, "campaign_id": 1, "piece_id": 1, "user_id": "60942e38-5094-4f00-b5e6-6d4b3d0bc8af", "user_name": "Bob Creator", "action": "edited", "version_no": 2, "detail ...(truncated)

### TC-002 - Change-request notes and regenerations are logged  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/activity`  |  **User story:** US13, US9
- **Input:** as Bob Creator (bob); path /api/v1/content/3/activity
- **Expected:** HTTP 200; 1.action = "changes_requested"; 1.detail.feedback = "Stronger CTA please."; 1.version_no = 1; 2.action = "regenerated"; 2.version_no = 2
- **Actual:** HTTP 200 [{"id": 10, "campaign_id": 1, "piece_id": 3, "user_id": "e8f790c8-4a25-4d55-a310-1915ffd9df74", "user_name": "Bob Creator", "action": "generated", "version_no": 1, "detail": {"platform": "facebook", "job_id": 1}, "created_at": "2026-11-24T18:35:52.839480"}, {"id": 12, "campaign_id": 1, "piece_id": 3, "user_id": "10d7e7eb-4d7e-4b88-9e55-9f15c90129b7", "user_name": "Carol Reviewer", "action": "changes_requested", "vers ...(truncated)

### TC-003 - The rejection and its reason are logged  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/activity`  |  **User story:** US13, US8
- **Input:** as Bob Creator (bob); path /api/v1/content/1/activity
- **Expected:** HTTP 200; 1.action = "rejected"; 1.detail.reason = "Not suitable for our audience."
- **Actual:** HTTP 200 [{"id": 8, "campaign_id": 1, "piece_id": 1, "user_id": "0e2ad110-cd5b-4692-844f-b71933130d56", "user_name": "Bob Creator", "action": "generated", "version_no": 1, "detail": {"platform": "blog", "job_id": 1}, "created_at": "2026-11-24T18:35:52.885297"}, {"id": 12, "campaign_id": 1, "piece_id": 1, "user_id": "84321d1d-1dd2-4dcd-b983-9dd808bfbb60", "user_name": "Carol Reviewer", "action": "rejected", "version_no": 1, "d ...(truncated)

### TC-004 - Outsider gets 404 for a piece's log  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/activity`  |  **User story:** US13
- **Input:** as Eve Outsider (eve); path /api/v1/content/1/activity
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-005 - Owner sees the campaign log, newest first  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/activity`  |  **User story:** US13
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/activity
- **Expected:** HTTP 200; 0.action = "approved"; 0.user_name = "Carol Reviewer"
- **Actual:** HTTP 200 [{"id": 12, "campaign_id": 1, "piece_id": 1, "user_id": "059ca3c3-c264-4c62-a12d-d23f82dc292e", "user_name": "Carol Reviewer", "action": "approved", "version_no": 1, "detail": null, "created_at": "2026-11-24T18:35:52.984048"}, {"id": 11, "campaign_id": 1, "piece_id": 4, "user_id": "1e0b32d1-f2c6-4282-94f5-cd31ddc55649", "user_name": "Bob Creator", "action": "generated", "version_no": 1, "detail": {"platform": "instag ...(truncated)

### TC-006 - Creators cannot read the campaign-wide log  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/activity`  |  **User story:** US13
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/activity
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: owner.", "code": "FORBIDDEN"}

### TC-007 - A global admin can read any campaign's log  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/activity`  |  **User story:** US13
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns/1/activity
- **Expected:** HTTP 200; 0.action = <present>
- **Actual:** HTTP 200 [{"id": 11, "campaign_id": 1, "piece_id": 4, "user_id": "e24c48e7-353f-4914-b965-d0c736a55684", "user_name": "Bob Creator", "action": "generated", "version_no": 1, "detail": {"platform": "instagram", "job_id": 1}, "created_at": "2026-11-24T18:35:53.068562"}, {"id": 10, "campaign_id": 1, "piece_id": 3, "user_id": "e24c48e7-353f-4914-b965-d0c736a55684", "user_name": "Bob Creator", "action": "generated", "version_no": 1 ...(truncated)

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
- **Expected:** HTTP 200; name = "Alice Owner"; email = "alice@example.com"; role = "user"; id = "a5db4ee9-4ca2-4eb4-98f0-9288057aa118"
- **Actual:** HTTP 200 {"id": "a5db4ee9-4ca2-4eb4-98f0-9288057aa118", "name": "Alice Owner", "email": "alice@example.com", "role": "user"}

### TC-018 - Name falls back to the email prefix when the token has no name  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as custom token; path /api/v1/me
- **Expected:** HTTP 200; name = "bob"; email = "bob@example.com"
- **Actual:** HTTP 200 {"id": "38827a48-6750-486b-8864-6f16fe5dd1f5", "name": "bob", "email": "bob@example.com", "role": "user"}

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

### TC-024 - ES256 token signed with the project's signing key is accepted (JWKS verification)  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as custom token; path /api/v1/me
- **Expected:** HTTP 200; email = "alice@example.com"
- **Actual:** HTTP 200 {"id": "fad86225-b861-4b15-ae34-0036552238a4", "name": "Alice Owner", "email": "alice@example.com", "role": "user"}

### TC-025 - ES256 token signed with a different key (same key id) is rejected  `PASS`
- **API:** `GET /api/v1/me`
- **Input:** as custom token; path /api/v1/me
- **Expected:** HTTP 401; code = "UNAUTHORIZED"
- **Actual:** HTTP 401 {"detail": "Invalid token.", "code": "UNAUTHORIZED"}

### TC-026 - Create a brand with tone, preferred and avoided terms  `PASS`
- **API:** `POST /api/v1/brands`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands; body {"name": "Acme Tea", "tone": "friendly and calm", "preferred_terms": ["handpicked"], "avoided_terms": ["cheap"]}
- **Expected:** HTTP 201; name = "Acme Tea"; tone = "friendly and calm"; preferred_terms = ["handpicked"]; avoided_terms = ["cheap"]; owner_id = "dfc601a0-eaab-408d-9d33-2ef036bb5085"
- **Actual:** HTTP 201 {"id": 1, "owner_id": "dfc601a0-eaab-408d-9d33-2ef036bb5085", "name": "Acme Tea", "tone": "friendly and calm", "preferred_terms": ["handpicked"], "avoided_terms": ["cheap"], "updated_by": "dfc601a0-eaab-408d-9d33-2ef036bb5085", "created_at": "2026-11-24T18:35:54.350436Z", "updated_at": "2026-11-24T18:35:54.350438Z"}

### TC-027 - Brand without tone is rejected  `PASS`
- **API:** `POST /api/v1/brands`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands; body {"name": "No Tone"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "tone"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "tone", "message": "Field required"}]}

### TC-028 - Brand with a whitespace-only name is rejected  `PASS`
- **API:** `POST /api/v1/brands`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands; body {"name": "   ", "tone": "calm"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "name"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "name", "message": "String should have at least 1 character"}]}

### TC-029 - Same owner cannot create two brands with one name  `PASS`
- **API:** `POST /api/v1/brands`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands; body {"name": "Acme Tea", "tone": "friendly and calm", "preferred_terms": ["handpicked"], "avoided_terms": ["cheap"]}
- **Expected:** HTTP 409; code = "DUPLICATE"
- **Actual:** HTTP 409 {"detail": "You already have a brand with this name.", "code": "DUPLICATE"}

### TC-030 - Blank and repeated terms are dropped from the term lists  `PASS`
- **API:** `POST /api/v1/brands`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands; body {"name": "Acme Tea", "tone": "friendly and calm", "preferred_terms": [" organic ", "", "organic", "local"], "avoided_terms": ["cheap"]}
- **Expected:** HTTP 201; preferred_terms = ["organic", "local"]
- **Actual:** HTTP 201 {"id": 1, "owner_id": "fb4e63fd-7757-4f4a-a0f2-64909af43f7f", "name": "Acme Tea", "tone": "friendly and calm", "preferred_terms": ["organic", "local"], "avoided_terms": ["cheap"], "updated_by": "fb4e63fd-7757-4f4a-a0f2-64909af43f7f", "created_at": "2026-11-24T18:35:54.409101Z", "updated_at": "2026-11-24T18:35:54.409102Z"}

### TC-031 - Owner and campaign members see the brand; an outsider sees none  `PASS`
- **API:** `GET /api/v1/brands`  |  **User story:** US5, US11
- **Input:** as Bob Creator (bob); path /api/v1/brands
- **Expected:** HTTP 200; 0.name = "GreenLeaf Organics"
- **Actual:** HTTP 200 [{"id": 1, "owner_id": "13f22312-1508-49fd-91e4-e6fd4a71d0b0", "name": "GreenLeaf Organics", "tone": "warm, practical, no jargon", "preferred_terms": ["organic", "sustainable"], "avoided_terms": ["cheap", "chemical"], "updated_by": "13f22312-1508-49fd-91e4-e6fd4a71d0b0", "created_at": "2026-11-24T18:35:54.430067", "updated_at": "2026-11-24T18:35:54.430067"}]

### TC-032 - Owner and campaign members see the brand; an outsider sees none  `PASS`
- **API:** `GET /api/v1/brands`  |  **User story:** US5, US11
- **Input:** as Eve Outsider (eve); path /api/v1/brands
- **Expected:** HTTP 200; response body == []
- **Actual:** HTTP 200 []

### TC-033 - Outsider gets 404 for someone else's brand  `PASS`
- **API:** `GET /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Eve Outsider (eve); path /api/v1/brands/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brand not found.", "code": "NOT_FOUND"}

### TC-034 - Campaign member can read the brand guidelines  `PASS`
- **API:** `GET /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Carol Reviewer (carol); path /api/v1/brands/1
- **Expected:** HTTP 200; name = "GreenLeaf Organics"
- **Actual:** HTTP 200 {"id": 1, "owner_id": "9cc7725b-b582-4053-ab5b-d4c193361e32", "name": "GreenLeaf Organics", "tone": "warm, practical, no jargon", "preferred_terms": ["organic", "sustainable"], "avoided_terms": ["cheap", "chemical"], "updated_by": "9cc7725b-b582-4053-ab5b-d4c193361e32", "created_at": "2026-11-24T18:35:54.501143", "updated_at": "2026-11-24T18:35:54.501143"}

### TC-035 - Brand manager of a campaign can edit the brand tone  `PASS`
- **API:** `PATCH /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Dave BrandManager (dave); path /api/v1/brands/1; body {"tone": "bold and playful"}
- **Expected:** HTTP 200; tone = "bold and playful"; updated_by = "260d2e8b-c5af-4feb-b050-b30078cb2aa8"
- **Actual:** HTTP 200 {"id": 1, "owner_id": "0ea645b7-e577-479b-a0de-350194baa1ab", "name": "GreenLeaf Organics", "tone": "bold and playful", "preferred_terms": ["organic", "sustainable"], "avoided_terms": ["cheap", "chemical"], "updated_by": "260d2e8b-c5af-4feb-b050-b30078cb2aa8", "created_at": "2026-11-24T18:35:54.535301", "updated_at": "2026-11-24T18:35:54.550276Z"}

### TC-036 - Creator cannot edit brand guidelines  `PASS`
- **API:** `PATCH /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Bob Creator (bob); path /api/v1/brands/1; body {"tone": "x"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "Only the brand owner or a brand manager can edit a brand.", "code": "FORBIDDEN"}

### TC-037 - Outsider cannot even see the brand to edit it  `PASS`
- **API:** `PATCH /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Eve Outsider (eve); path /api/v1/brands/1; body {"tone": "x"}
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brand not found.", "code": "NOT_FOUND"}

### TC-038 - PATCH with an empty body is rejected  `PASS`
- **API:** `PATCH /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands/1; body {}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "", "message": "Value error, Provide at least one field to update."}]}

### TC-039 - Renaming a brand to another brand's name (same owner) is rejected  `PASS`
- **API:** `PATCH /api/v1/brands/{brand_id}`  |  **User story:** US5
- **Input:** as Alice Owner (alice); path /api/v1/brands/1; body {"name": "Acme Tea"}
- **Expected:** HTTP 409; code = "DUPLICATE"
- **Actual:** HTTP 409 {"detail": "A brand with this name already exists.", "code": "DUPLICATE"}

### TC-040 - Brand changes apply only to content generated afterwards  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US5, US3
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1
- **Expected:** HTTP 200; current_version.body = "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from recycled material\n\n## What to do next\nTone: warm, practical, no jargon. Key terms: organic, sustainable.\n\n## Conclusion\nDrive pre-orders of the compost kit"; current_version.version_no = 1
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "af909150-fdbb-4c6e-a71f-1c061ae8a45b", "created_at": "2026-11-24T18:35:54.725820", "updated_at": "2026-11-24T18:35:54.726173", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made  ...(truncated)

### TC-041 - Creator submits a brief; the brand tone is used by default  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 201; topic = "Spring Compost Kit"; status = "draft"; tone = null; effective_tone = "warm, practical, no jargon"; platforms = ["blog", "linkedin", "facebook", "instagram"]; created_by = "747902e1-37bf-4ea4-9131-6fb268edfd52"
- **Actual:** HTTP 201 {"id": 1, "campaign_id": 1, "created_by": "747902e1-37bf-4ea4-9131-6fb268edfd52", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog", "linkedin", "facebook", "instagram"], "status": "draft", "created_at ...(truncated)

### TC-042 - A brief can override the brand tone for itself only  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"], "tone": "urgent"}
- **Expected:** HTTP 201; tone = "urgent"; effective_tone = "urgent"
- **Actual:** HTTP 201 {"id": 1, "campaign_id": 1, "created_by": "661be3f2-0944-4de8-be5c-55f850900aff", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": "urgent", "effective_tone": "urgent", "platforms": ["blog", "linkedin", "facebook", "instagram"], "status": "draft", "created_at": "2026-11-24T1 ...(truncated)

### TC-043 - Audience and key messages are optional  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/briefs; body {"topic": "T", "objective": "O", "platforms": ["blog"]}
- **Expected:** HTTP 201; target_audience = null; key_messages = null
- **Actual:** HTTP 201 {"id": 1, "campaign_id": 1, "created_by": "9ec8e62f-0762-4213-8b43-9c856d951fa8", "topic": "T", "objective": "O", "target_audience": null, "key_messages": null, "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog"], "status": "draft", "created_at": "2026-11-24T18:35:54.840029Z", "updated_at": "2026-11-24T18:35:54.840029Z"}

### TC-044 - Repeated platforms are stored once  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "blog", "facebook"]}
- **Expected:** HTTP 201; platforms = ["blog", "facebook"]
- **Actual:** HTTP 201 {"id": 1, "campaign_id": 1, "created_by": "65e0c101-97df-4b39-97d2-93b918ebcbe4", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog", "facebook"], "status": "draft", "created_at": "2026-11-24T18:35:54.8 ...(truncated)

### TC-045 - Brief without a topic is rejected  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "topic"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "topic", "message": "Field required"}]}

### TC-046 - Brief with an empty platform list is rejected  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": []}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "platforms"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "platforms", "message": "List should have at least 1 item after validation, not 0"}]}

### TC-047 - Only blog, linkedin, facebook and instagram are accepted  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["twitter"]}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "platforms.0", "message": "Input should be 'blog', 'linkedin', 'facebook' or 'instagram'"}]}

### TC-048 - A whitespace-only objective is rejected  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "  ", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "objective"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "objective", "message": "String should have at least 1 character"}]}

### TC-049 - Reviewers cannot create briefs  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Carol Reviewer (carol); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner.", "code": "FORBIDDEN"}

### TC-050 - Brand managers cannot create briefs  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1
- **Input:** as Dave BrandManager (dave); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner.", "code": "FORBIDDEN"}

### TC-051 - Outsider gets 404 for the campaign  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1, US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns/1/briefs; body {"topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "platforms": ["blog", "linkedin", "facebook", "instagram"]}
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Campaign not found.", "code": "NOT_FOUND"}

### TC-052 - A saved brief can be edited until generation starts  `PASS`
- **API:** `PATCH /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1; body {"topic": "New Topic", "platforms": ["blog"]}
- **Expected:** HTTP 200; topic = "New Topic"; platforms = ["blog"]; status = "draft"
- **Actual:** HTTP 200 {"id": 1, "campaign_id": 1, "created_by": "da8db281-9bda-425e-ab92-27a2c6733f9e", "topic": "New Topic", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog"], "status": "draft", "created_at": "2026-11-24T18:35:55.153521", "updated_at": ...(truncated)

### TC-053 - PATCH with no fields is rejected  `PASS`
- **API:** `PATCH /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1; body {}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "", "message": "Value error, Provide at least one field to update."}]}

### TC-054 - A required field cannot be set to null  `PASS`
- **API:** `PATCH /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1; body {"topic": null}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "", "message": "Value error, topic cannot be null."}]}

### TC-055 - Briefs cannot be edited once generation has run  `PASS`
- **API:** `PATCH /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1; body {"topic": "Too late"}
- **Expected:** HTTP 409; code = "BRIEF_LOCKED"
- **Actual:** HTTP 409 {"detail": "The brief can no longer be edited because generation has started.", "code": "BRIEF_LOCKED"}

### TC-056 - Reviewers cannot edit briefs  `PASS`
- **API:** `PATCH /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Carol Reviewer (carol); path /api/v1/briefs/1; body {"topic": "x"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner.", "code": "FORBIDDEN"}

### TC-057 - Reviewer can read the brief next to the content  `PASS`
- **API:** `GET /api/v1/briefs/{brief_id}`  |  **User story:** US6
- **Input:** as Carol Reviewer (carol); path /api/v1/briefs/1
- **Expected:** HTTP 200; topic = "Spring Compost Kit"
- **Actual:** HTTP 200 {"id": 1, "campaign_id": 1, "created_by": "14409104-8040-4863-bdf0-3508c1f18c4d", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog", "linkedin", "facebook", "instagram"], "status": "draft", "created_at ...(truncated)

### TC-058 - Outsider gets 404 for a brief  `PASS`
- **API:** `GET /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Eve Outsider (eve); path /api/v1/briefs/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brief not found.", "code": "NOT_FOUND"}

### TC-059 - Members list the briefs of a campaign  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/briefs`  |  **User story:** US1, US11
- **Input:** as Carol Reviewer (carol); path /api/v1/campaigns/1/briefs
- **Expected:** HTTP 200; 0.id = 1
- **Actual:** HTTP 200 [{"id": 1, "campaign_id": 1, "created_by": "521a146c-09e3-4ad6-97fb-f44a0ced5b1b", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog", "linkedin", "facebook", "instagram"], "status": "draft", "created_a ...(truncated)

### TC-060 - Unknown brief id returns 404  `PASS`
- **API:** `GET /api/v1/briefs/{brief_id}`  |  **User story:** US1
- **Input:** as Alice Owner (alice); path /api/v1/briefs/9999
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brief not found.", "code": "NOT_FOUND"}

### TC-061 - Create a campaign under an own brand; the creator becomes owner  `PASS`
- **API:** `POST /api/v1/campaigns`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns; body {"brand_id": 1, "name": "Autumn Sale"}
- **Expected:** HTTP 201; name = "Autumn Sale"; my_role = "owner"; brand_name = "GreenLeaf Organics"
- **Actual:** HTTP 201 {"id": 2, "brand_id": 1, "brand_name": "GreenLeaf Organics", "name": "Autumn Sale", "description": null, "created_at": "2026-11-24T18:35:55.480942Z", "my_role": "owner"}

### TC-062 - Cannot create a campaign on somebody else's brand  `PASS`
- **API:** `POST /api/v1/campaigns`  |  **User story:** US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns; body {"brand_id": 1, "name": "Hijack"}
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brand not found.", "code": "NOT_FOUND"}

### TC-063 - Campaign without a name is rejected  `PASS`
- **API:** `POST /api/v1/campaigns`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns; body {"brand_id": 1}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "name"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "name", "message": "Field required"}]}

### TC-064 - Members list their campaign with their role; outsiders see nothing  `PASS`
- **API:** `GET /api/v1/campaigns`  |  **User story:** US11
- **Input:** as Carol Reviewer (carol); path /api/v1/campaigns
- **Expected:** HTTP 200; 0.my_role = "reviewer"; 0.id = 1
- **Actual:** HTTP 200 [{"id": 1, "brand_id": 1, "brand_name": "GreenLeaf Organics", "name": "Spring Launch", "description": "Spring product launch", "created_at": "2026-11-24T18:35:55.572627", "my_role": "reviewer"}]

### TC-065 - Members list their campaign with their role; outsiders see nothing  `PASS`
- **API:** `GET /api/v1/campaigns`  |  **User story:** US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns
- **Expected:** HTTP 200; response body == []
- **Actual:** HTTP 200 []

### TC-066 - Non-member cannot see that a campaign exists  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}`  |  **User story:** US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Campaign not found.", "code": "NOT_FOUND"}

### TC-067 - Member can read the campaign  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1
- **Expected:** HTTP 200; my_role = "creator"; name = "Spring Launch"
- **Actual:** HTTP 200 {"id": 1, "brand_id": 1, "brand_name": "GreenLeaf Organics", "name": "Spring Launch", "description": "Spring product launch", "created_at": "2026-11-24T18:35:55.641458", "my_role": "creator"}

### TC-068 - Member list contains the owner and all added members with one role each  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members
- **Expected:** HTTP 200; 0.member_role = "owner"; 0.email = "alice@example.com"
- **Actual:** HTTP 200 [{"user_id": "ca4cf296-84b6-4af7-bb28-c5c2ebec2b3a", "name": "Alice Owner", "email": "alice@example.com", "member_role": "owner", "joined_at": "2026-11-24T18:35:55.674885"}, {"user_id": "1dd417b0-8ae7-4d6d-bd77-27a0ab1e625f", "name": "Bob Creator", "email": "bob@example.com", "member_role": "creator", "joined_at": "2026-11-24T18:35:55.677137"}, {"user_id": "2f46b60e-1e26-48d4-a4d9-8048ee17f0db", "name": "Carol Review ...(truncated)

### TC-069 - campaign has 5 members (owner + 4 added)  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/members`
- **Input:** -
- **Expected:** 5
- **Actual:** 5

### TC-070 - Outsider cannot list members  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns/1/members
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Campaign not found.", "code": "NOT_FOUND"}

### TC-071 - Owner adds a registered user as reviewer  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11, US6
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members; body {"email": "EVE@example.com", "member_role": "reviewer"}
- **Expected:** HTTP 201; member_role = "reviewer"; email = "eve@example.com"; name = "Eve Outsider"
- **Actual:** HTTP 201 {"user_id": "3eb96fc6-b39c-4455-99b2-f72177aa7aa2", "name": "Eve Outsider", "email": "eve@example.com", "member_role": "reviewer", "joined_at": "2026-11-24T18:35:55.755072Z"}

### TC-072 - Only owners can add members  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/members; body {"email": "eve@example.com", "member_role": "reviewer"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: owner.", "code": "FORBIDDEN"}

### TC-073 - Adding an email that never signed in returns 404 USER_NOT_FOUND  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members; body {"email": "ghost@example.com", "member_role": "creator"}
- **Expected:** HTTP 404; code = "USER_NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "No user with that email. Ask them to sign in to the app once first.", "code": "USER_NOT_FOUND"}

### TC-074 - A user has only one role per campaign  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members; body {"email": "bob@example.com", "member_role": "reviewer"}
- **Expected:** HTTP 409; code = "ALREADY_MEMBER"
- **Actual:** HTTP 409 {"detail": "That user is already a member of this campaign.", "code": "ALREADY_MEMBER"}

### TC-075 - Only the four campaign roles are accepted  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members; body {"email": "eve@example.com", "member_role": "admin"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "member_role"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "member_role", "message": "Input should be 'owner', 'creator', 'reviewer' or 'brand_manager'"}]}

### TC-076 - Invalid email address is rejected  `PASS`
- **API:** `POST /api/v1/campaigns/{campaign_id}/members`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members; body {"email": "not-an-email", "member_role": "creator"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "email"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "email", "message": "Value error, Not a valid email address."}]}

### TC-077 - A campaign always keeps at least one owner  `PASS`
- **API:** `DELETE /api/v1/campaigns/{campaign_id}/members/{user_id}`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members/bd383661-06ca-4c55-be63-1bc47029aed8
- **Expected:** HTTP 409; code = "LAST_OWNER"
- **Actual:** HTTP 409 {"detail": "A campaign must keep at least one owner.", "code": "LAST_OWNER"}

### TC-078 - Removing a member revokes access immediately  `PASS`
- **API:** `DELETE /api/v1/campaigns/{campaign_id}/members/{user_id}`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members/263db953-ce94-4614-bcac-826fd54f98a8
- **Expected:** HTTP 204
- **Actual:** HTTP 204

### TC-079 - Removing a member revokes access immediately  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Campaign not found.", "code": "NOT_FOUND"}

### TC-080 - Creator cannot remove members  `PASS`
- **API:** `DELETE /api/v1/campaigns/{campaign_id}/members/{user_id}`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/members/1de8a85f-8644-4c23-83b9-f0fccad18bb7
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: owner.", "code": "FORBIDDEN"}

### TC-081 - Removing a user who is not a member returns 404  `PASS`
- **API:** `DELETE /api/v1/campaigns/{campaign_id}/members/{user_id}`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members/7e9abc45-8872-4cdc-8408-4e0af32146c6
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Member not found.", "code": "NOT_FOUND"}

### TC-082 - Malformed member id returns 404, not a server error  `PASS`
- **API:** `DELETE /api/v1/campaigns/{campaign_id}/members/{user_id}`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/1/members/not-a-uuid
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Member not found.", "code": "NOT_FOUND"}

### TC-083 - Non-numeric path id is a validation error  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}`  |  **User story:** US11
- **Input:** as Alice Owner (alice); path /api/v1/campaigns/abc
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "campaign_id", "message": "Input should be a valid integer, unable to parse string as an integer"}]}

### TC-084 - Filter a campaign's content by status  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US10
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/content; query {"status": "approved"}
- **Expected:** HTTP 200; 0.platform = "blog"
- **Actual:** HTTP 200 [{"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "approved", "created_by": "38f5de85-59a9-4607-a82e-ef0566cf034c", "created_at": "2026-11-24T18:35:56.145933", "updated_at": "2026-11-24T18:35:56.150197", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from  ...(truncated)

### TC-085 - one approved piece  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`
- **Input:** -
- **Expected:** 1
- **Actual:** 1

### TC-086 - Filter a campaign's content by status  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US10
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/content; query {"status": "rejected"}
- **Expected:** HTTP 200; 0.platform = "linkedin"; 0.rejection_reason = "Wording is off-brand."
- **Actual:** HTTP 200 [{"id": 2, "brief_id": 1, "campaign_id": 1, "platform": "linkedin", "status": "rejected", "created_by": "38f5de85-59a9-4607-a82e-ef0566cf034c", "created_at": "2026-11-24T18:35:56.146334", "updated_at": "2026-11-24T18:35:56.153164", "current_version": {"id": 2, "version_no": 1, "body": "Spring Compost Kit: what urban gardeners should know.\n\nEasy, odour-free, made from recycled material\n\nKey terms: organic, sustain ...(truncated)

### TC-087 - two pending pieces  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`
- **Input:** -
- **Expected:** 2
- **Actual:** 2

### TC-088 - Filter a campaign's content by platform  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US10
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/content; query {"platform": "instagram"}
- **Expected:** HTTP 200; 0.platform = "instagram"
- **Actual:** HTTP 200 [{"id": 4, "brief_id": 1, "campaign_id": 1, "platform": "instagram", "status": "pending_review", "created_by": "2e10e825-1232-4ac4-965e-3bc818a48bd0", "created_at": "2026-11-24T18:35:56.199017", "updated_at": "2026-11-24T18:35:56.199361", "current_version": {"id": 4, "version_no": 1, "body": "Spring Compost Kit | Easy, odour-free, made from recycled material\n\n#spring #brand #campaign", "creative_suggestion": "Brigh ...(truncated)

### TC-089 - one instagram piece  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`
- **Input:** -
- **Expected:** 1
- **Actual:** 1

### TC-090 - Unknown status value is a validation error  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US10
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/content; query {"status": "published"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "status", "message": "Input should be 'draft', 'pending_review', 'approved' or 'rejected'"}]}

### TC-091 - Outsider gets 404 when listing a campaign's content  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US10, US11
- **Input:** as Eve Outsider (eve); path /api/v1/campaigns/1/content
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Campaign not found.", "code": "NOT_FOUND"}

### TC-092 - Reviewer opens a piece next to its brief  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US6
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1
- **Expected:** HTTP 200; brief.topic = "Spring Compost Kit"; brief.key_messages = <present>; versions.0.version_no = 1; current_version.version_no = 1
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "5767683a-73eb-4285-abd1-8651f5288c0a", "created_at": "2026-11-24T18:35:56.320390", "updated_at": "2026-11-24T18:35:56.320745", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made  ...(truncated)

### TC-093 - Outsider gets 404 for a piece  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US6
- **Input:** as Eve Outsider (eve); path /api/v1/content/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-094 - Versions come back oldest first  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/versions`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/versions
- **Expected:** HTTP 200; 0.version_no = 1; 0.origin = "ai_generated"; 1.version_no = 2; 1.origin = "human_edit"
- **Actual:** HTTP 200 [{"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from recycled material\n\n## What to do next\nTone: warm, practical, no jargon. Key terms: organic, sustainable.\n\n## Conclusion\nDrive pre-orders of the compost kit", "creative_suggestion": null, "origin": "ai_generated", "model_name": "fake-llm-v1" ...(truncated)

### TC-095 - An edit is saved as a new human_edit version  `PASS`
- **API:** `PATCH /api/v1/content/{piece_id}`  |  **User story:** US6, US13
- **Input:** as Bob Creator (bob); path /api/v1/content/1; body {"body": "My improved blog text"}
- **Expected:** HTTP 200; status = "pending_review"; current_version.version_no = 2; current_version.origin = "human_edit"; current_version.body = "My improved blog text"; current_version.created_by = "a77067bf-fc38-4809-bfca-4fcdf2068d92"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "a77067bf-fc38-4809-bfca-4fcdf2068d92", "created_at": "2026-11-24T18:35:56.446460", "updated_at": "2026-11-24T18:35:56.451005", "current_version": {"id": 5, "version_no": 2, "body": "My improved blog text", "creative_suggestion": null, "origin": "human_edit", "model_name": null, "flags": null, "created_by": "a7706 ...(truncated)

### TC-096 - Editing an approved piece sends it back to pending review  `PASS`
- **API:** `PATCH /api/v1/content/{piece_id}`  |  **User story:** US6
- **Input:** as Bob Creator (bob); path /api/v1/content/1; body {"body": "Changed after approval"}
- **Expected:** HTTP 200; status = "pending_review"; current_version.version_no = 2
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "1127ce18-a196-43e0-bde6-4b94084cc8f7", "created_at": "2026-11-24T18:35:56.489563", "updated_at": "2026-11-24T18:35:56.497141", "current_version": {"id": 5, "version_no": 2, "body": "Changed after approval", "creative_suggestion": null, "origin": "human_edit", "model_name": null, "flags": null, "created_by": "1127 ...(truncated)

### TC-097 - Edit with an empty body is refused  `PASS`
- **API:** `PATCH /api/v1/content/{piece_id}`  |  **User story:** US6
- **Input:** as Bob Creator (bob); path /api/v1/content/1; body {"body": "  "}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "body"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "body", "message": "String should have at least 1 character"}]}

### TC-098 - Brand managers cannot edit content  `PASS`
- **API:** `PATCH /api/v1/content/{piece_id}`  |  **User story:** US6
- **Input:** as Dave BrandManager (dave); path /api/v1/content/1; body {"body": "x"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner, reviewer.", "code": "FORBIDDEN"}

### TC-099 - Deleting without the confirmation flag is refused  `PASS`
- **API:** `DELETE /api/v1/content/{piece_id}`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/content/1
- **Expected:** HTTP 400; code = "CONFIRMATION_REQUIRED"
- **Actual:** HTTP 400 {"detail": "Deleting content needs confirmation: repeat the request with ?confirm=true.", "code": "CONFIRMATION_REQUIRED"}

### TC-100 - Deleting without the confirmation flag is refused  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US11
- **Input:** as Bob Creator (bob); path /api/v1/content/1
- **Expected:** HTTP 200; status = "pending_review"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "9738dff9-3324-4b16-b547-ece03dea1b76", "created_at": "2026-11-24T18:35:56.620538", "updated_at": "2026-11-24T18:35:56.620884", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made  ...(truncated)

### TC-101 - Confirmed delete hides the piece; versions and log are kept  `PASS`
- **API:** `DELETE /api/v1/content/{piece_id}`  |  **User story:** US11, US13
- **Input:** as Bob Creator (bob); path /api/v1/content/1; query {"confirm": "true"}
- **Expected:** HTTP 204
- **Actual:** HTTP 204

### TC-102 - Confirmed delete hides the piece; versions and log are kept  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US11, US13
- **Input:** as Bob Creator (bob); path /api/v1/content/1
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-103 - deleted piece is not listed  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`
- **Input:** -
- **Expected:** false
- **Actual:** false

### TC-104 - version rows are kept  `PASS`
- **API:** `database check`
- **Input:** -
- **Expected:** 1
- **Actual:** 1

### TC-105 - deletion is logged  `PASS`
- **API:** `database check`
- **Input:** -
- **Expected:** 1
- **Actual:** 1

### TC-106 - Reviewers cannot delete content  `PASS`
- **API:** `DELETE /api/v1/content/{piece_id}`  |  **User story:** US11
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1; query {"confirm": "true"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner.", "code": "FORBIDDEN"}

### TC-107 - Any member can comment on a piece  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/comments`  |  **User story:** US6, US8
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/comments; body {"body": "Please cite the source."}
- **Expected:** HTTP 201; body = "Please cite the source."; author_name = "Carol Reviewer"; user_id = "36a49c34-589e-4b45-a0e1-94eea39780e6"
- **Actual:** HTTP 201 {"id": 1, "piece_id": 1, "user_id": "36a49c34-589e-4b45-a0e1-94eea39780e6", "author_name": "Carol Reviewer", "body": "Please cite the source.", "created_at": "2026-11-24T18:35:56.756001Z"}

### TC-108 - Any member can comment on a piece  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/comments`  |  **User story:** US6, US8
- **Input:** as Bob Creator (bob); path /api/v1/content/1/comments; body {"body": "Added in the next draft."}
- **Expected:** HTTP 201
- **Actual:** HTTP 201 {"id": 2, "piece_id": 1, "user_id": "15cae560-e7bf-4d3c-8c9a-b1a644986430", "author_name": "Bob Creator", "body": "Added in the next draft.", "created_at": "2026-11-24T18:35:56.758190Z"}

### TC-109 - Any member can comment on a piece  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/comments`  |  **User story:** US6, US8
- **Input:** as Dave BrandManager (dave); path /api/v1/content/1/comments
- **Expected:** HTTP 200; 0.author_name = "Carol Reviewer"; 1.author_name = "Bob Creator"
- **Actual:** HTTP 200 [{"id": 1, "piece_id": 1, "user_id": "36a49c34-589e-4b45-a0e1-94eea39780e6", "author_name": "Carol Reviewer", "body": "Please cite the source.", "created_at": "2026-11-24T18:35:56.756001"}, {"id": 2, "piece_id": 1, "user_id": "15cae560-e7bf-4d3c-8c9a-b1a644986430", "author_name": "Bob Creator", "body": "Added in the next draft.", "created_at": "2026-11-24T18:35:56.758190"}]

### TC-110 - Blank comment is refused  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/comments`  |  **User story:** US6
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/comments; body {"body": "   "}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "body"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "body", "message": "String should have at least 1 character"}]}

### TC-111 - Outsider cannot comment or read comments  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/comments`  |  **User story:** US6
- **Input:** as Eve Outsider (eve); path /api/v1/content/1/comments; body {"body": "hi"}
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-112 - Outsider cannot comment or read comments  `PASS`
- **API:** `GET /api/v1/content/{piece_id}/comments`  |  **User story:** US6
- **Input:** as Eve Outsider (eve); path /api/v1/content/1/comments
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-113 - Dashboard counts pieces per status, in total and per campaign  `PASS`
- **API:** `GET /api/v1/dashboard`  |  **User story:** US10
- **Input:** as Bob Creator (bob); path /api/v1/dashboard
- **Expected:** HTTP 200; totals.approved = 1; totals.rejected = 1; totals.pending_review = 2; campaigns.0.counts.approved = 1; campaigns.0.campaign_id = 1
- **Actual:** HTTP 200 {"totals": {"draft": 0, "pending_review": 2, "approved": 1, "rejected": 1}, "campaigns": [{"campaign_id": 1, "name": "Spring Launch", "counts": {"draft": 0, "pending_review": 2, "approved": 1, "rejected": 1}}]}

### TC-114 - A user without campaigns gets an empty dashboard  `PASS`
- **API:** `GET /api/v1/dashboard`  |  **User story:** US10
- **Input:** as Eve Outsider (eve); path /api/v1/dashboard
- **Expected:** HTTP 200; totals.pending_review = 0; campaigns = []
- **Actual:** HTTP 200 {"totals": {"draft": 0, "pending_review": 0, "approved": 0, "rejected": 0}, "campaigns": []}

### TC-115 - One brief generates a pending-review piece for every selected platform  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1/generate
- **Expected:** HTTP 201; job.status = "done"; job.error_message = null; pieces.0.platform = "blog"; pieces.0.status = "pending_review"; pieces.0.current_version.version_no = 1; pieces.0.current_version.origin = "ai_generated"; pieces.3.platform = "instagram"
- **Actual:** HTTP 201 {"job": {"id": 1, "brief_id": 1, "platform": null, "status": "done", "error_message": null, "feedback_note": null, "created_at": "2026-11-24T18:35:56.936100Z", "finished_at": "2026-11-24T18:35:56.937865Z"}, "pieces": [{"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "261d002d-e27f-454a-87a1-3e1c22305094", "created_at": "2026-11-24T18:35:56.936808Z", "updated_at" ...(truncated)

### TC-116 - four pieces created  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`
- **Input:** -
- **Expected:** 4
- **Actual:** 4

### TC-117 - Instagram content comes with a creative suggestion  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US3
- **Input:** as Carol Reviewer (carol); path /api/v1/content/4
- **Expected:** HTTP 200; current_version.creative_suggestion = <present>; platform = "instagram"
- **Actual:** HTTP 200 {"id": 4, "brief_id": 1, "campaign_id": 1, "platform": "instagram", "status": "pending_review", "created_by": "583bb54b-0a85-4aa6-8baa-d876dcf67d4d", "created_at": "2026-11-24T18:35:56.976655", "updated_at": "2026-11-24T18:35:56.977009", "current_version": {"id": 4, "version_no": 1, "body": "Spring Compost Kit | Easy, odour-free, made from recycled material\n\n#spring #brand #campaign", "creative_suggestion": "Bright ...(truncated)

### TC-118 - Generation is fed the brand's preferred terms  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US3, US5
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1
- **Expected:** HTTP 200; current_version.body = contains 'organic'
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "0fb5b604-13f4-4094-a180-f57a98be06f2", "created_at": "2026-11-24T18:35:57.016574", "updated_at": "2026-11-24T18:35:57.016906", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made  ...(truncated)

### TC-119 - Only the platforms in the brief are generated  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3, US1
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1/generate
- **Expected:** HTTP 201; pieces.0.platform = "facebook"
- **Actual:** HTTP 201 {"job": {"id": 1, "brief_id": 1, "platform": null, "status": "done", "error_message": null, "feedback_note": null, "created_at": "2026-11-24T18:35:57.057353Z", "finished_at": "2026-11-24T18:35:57.058003Z"}, "pieces": [{"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "facebook", "status": "pending_review", "created_by": "46d9ed4d-d13e-4fbb-8fa9-af0a49b1b6c1", "created_at": "2026-11-24T18:35:57.057767Z", "updated ...(truncated)

### TC-120 - exactly one piece  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`
- **Input:** -
- **Expected:** 1
- **Actual:** 1

### TC-121 - After generation nothing is approved: all four pieces await review  `PASS`
- **API:** `GET /api/v1/dashboard`  |  **User story:** US3, US6
- **Input:** as Alice Owner (alice); path /api/v1/dashboard
- **Expected:** HTTP 200; totals.pending_review = 4; totals.approved = 0; totals.rejected = 0
- **Actual:** HTTP 200 {"totals": {"draft": 0, "pending_review": 4, "approved": 0, "rejected": 0}, "campaigns": [{"campaign_id": 1, "name": "Spring Launch", "counts": {"draft": 0, "pending_review": 4, "approved": 0, "rejected": 0}}]}

### TC-122 - A brief can only be generated once  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1/generate
- **Expected:** HTTP 409; code = "BRIEF_ALREADY_GENERATED"
- **Actual:** HTTP 409 {"detail": "Content was already generated for this brief (status: generated).", "code": "BRIEF_ALREADY_GENERATED"}

### TC-123 - Reviewers cannot trigger generation  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Carol Reviewer (carol); path /api/v1/briefs/1/generate
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: creator, owner.", "code": "FORBIDDEN"}

### TC-124 - Outsider gets 404 for the brief  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Eve Outsider (eve); path /api/v1/briefs/1/generate
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brief not found.", "code": "NOT_FOUND"}

### TC-125 - Generating an unknown brief returns 404  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Alice Owner (alice); path /api/v1/briefs/9999/generate
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Brief not found.", "code": "NOT_FOUND"}

### TC-126 - AI failure returns 502, saves no piece, keeps the brief editable and allows a retry  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1/generate
- **Expected:** HTTP 502; code = "GENERATION_FAILED"; job_id = <present>
- **Actual:** HTTP 502 {"detail": "The AI provider failed; nothing was saved. You can retry.", "code": "GENERATION_FAILED", "job_id": 1}

### TC-127 - AI failure returns 502, saves no piece, keeps the brief editable and allows a retry  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/campaigns/1/content
- **Expected:** HTTP 200; response body == []
- **Actual:** HTTP 200 []

### TC-128 - AI failure returns 502, saves no piece, keeps the brief editable and allows a retry  `PASS`
- **API:** `GET /api/v1/briefs/{brief_id}`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1
- **Expected:** HTTP 200; status = "draft"
- **Actual:** HTTP 200 {"id": 1, "campaign_id": 1, "created_by": "3c4f9a55-c903-4d2a-b28a-d1ee59a6fe33", "topic": "Spring Compost Kit", "objective": "Drive pre-orders of the compost kit", "target_audience": "urban gardeners", "key_messages": "Easy, odour-free, made from recycled material", "tone": null, "effective_tone": "warm, practical, no jargon", "platforms": ["blog", "linkedin", "facebook", "instagram"], "status": "draft", "created_at ...(truncated)

### TC-129 - AI failure returns 502, saves no piece, keeps the brief editable and allows a retry  `PASS`
- **API:** `POST /api/v1/briefs/{brief_id}/generate`  |  **User story:** US3
- **Input:** as Bob Creator (bob); path /api/v1/briefs/1/generate
- **Expected:** HTTP 201; job.status = "done"
- **Actual:** HTTP 201 {"job": {"id": 2, "brief_id": 1, "platform": null, "status": "done", "error_message": null, "feedback_note": null, "created_at": "2026-11-24T18:35:57.285907Z", "finished_at": "2026-11-24T18:35:57.287453Z"}, "pieces": [{"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "3c4f9a55-c903-4d2a-b28a-d1ee59a6fe33", "created_at": "2026-11-24T18:35:57.286369Z", "updated_at" ...(truncated)

### TC-130 - log contains generation_failed  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/activity`
- **Input:** -
- **Expected:** true
- **Actual:** true

### TC-131 - Reviewer lists the pieces pending review in a campaign  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`  |  **User story:** US6
- **Input:** as Carol Reviewer (carol); path /api/v1/campaigns/1/content; query {"status": "pending_review"}
- **Expected:** HTTP 200; 0.status = "pending_review"
- **Actual:** HTTP 200 [{"id": 4, "brief_id": 1, "campaign_id": 1, "platform": "instagram", "status": "pending_review", "created_by": "7588d482-2771-489f-b9f2-0425d84cb0fa", "created_at": "2026-11-24T18:35:57.365029", "updated_at": "2026-11-24T18:35:57.365387", "current_version": {"id": 4, "version_no": 1, "body": "Spring Compost Kit | Easy, odour-free, made from recycled material\n\n#spring #brand #campaign", "creative_suggestion": "Brigh ...(truncated)

### TC-132 - four pending pieces  `PASS`
- **API:** `GET /api/v1/campaigns/{campaign_id}/content`
- **Input:** -
- **Expected:** 4
- **Actual:** 4

### TC-133 - Reviewer approves a pending piece  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/approve
- **Expected:** HTTP 200; status = "approved"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "approved", "created_by": "51310f6d-b480-45ae-93dc-fbde4d7eb4c2", "created_at": "2026-11-24T18:35:57.404537", "updated_at": "2026-11-24T18:35:57.408691", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from r ...(truncated)

### TC-134 - Reviewer approves a pending piece  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1
- **Expected:** HTTP 200; reviews.0.decision = "approved"; reviews.0.reviewer_id = "e9524b28-8f64-4b37-86d4-c2179ac84739"; reviews.0.created_at = <present>; reviews.0.version_no = 1
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "approved", "created_by": "51310f6d-b480-45ae-93dc-fbde4d7eb4c2", "created_at": "2026-11-24T18:35:57.404537", "updated_at": "2026-11-24T18:35:57.408691", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from r ...(truncated)

### TC-135 - A non-reviewer (creator) trying to approve gets 403  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Bob Creator (bob); path /api/v1/content/1/approve
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: reviewer.", "code": "FORBIDDEN"}

### TC-136 - The campaign owner has no review rights (reviewer role only)  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Alice Owner (alice); path /api/v1/content/1/approve
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: reviewer.", "code": "FORBIDDEN"}

### TC-137 - Outsider gets 404 and cannot approve  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Eve Outsider (eve); path /api/v1/content/1/approve
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-138 - Approving an already approved piece is a conflict  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Frank Reviewer (frank); path /api/v1/content/1/approve
- **Expected:** HTTP 409; code = "INVALID_STATE"
- **Actual:** HTTP 409 {"detail": "Only pieces in pending_review can be reviewed (current status: approved).", "code": "INVALID_STATE"}

### TC-139 - A reviewer cannot approve a version they wrote themselves  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/approve
- **Expected:** HTTP 403; code = "SELF_REVIEW_FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "You cannot review content you created or edited.", "code": "SELF_REVIEW_FORBIDDEN"}

### TC-140 - A reviewer cannot approve a version they wrote themselves  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Frank Reviewer (frank); path /api/v1/content/1/approve
- **Expected:** HTTP 200; status = "approved"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "approved", "created_by": "d68ca19f-6e06-40be-96f4-11bfd1a250b5", "created_at": "2026-11-24T18:35:57.614086", "updated_at": "2026-11-24T18:35:57.622992", "current_version": {"id": 5, "version_no": 2, "body": "Carol's rewrite of the blog", "creative_suggestion": null, "origin": "human_edit", "model_name": null, "flags": null, "created_by": "fd06f ...(truncated)

### TC-141 - Approving version 1 after it was superseded by version 2 is refused  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/approve; body {"version_no": 1}
- **Expected:** HTTP 409; code = "STALE_VERSION"
- **Actual:** HTTP 409 {"detail": "You reviewed version 1, but the current version is 2.", "code": "STALE_VERSION"}

### TC-142 - Approving with the right version_no works  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1/approve; body {"version_no": 1}
- **Expected:** HTTP 200; status = "approved"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "approved", "created_by": "c6251f38-6107-407f-bd63-42410b423f79", "created_at": "2026-11-24T18:35:57.703846", "updated_at": "2026-11-24T18:35:57.708306", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made from r ...(truncated)

### TC-143 - Approving an unknown piece returns 404  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/9999/approve
- **Expected:** HTTP 404; code = "NOT_FOUND"
- **Actual:** HTTP 404 {"detail": "Content piece not found.", "code": "NOT_FOUND"}

### TC-144 - Reviewer rejects a piece with a reason; the creator can read it  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/reject`  |  **User story:** US8
- **Input:** as Carol Reviewer (carol); path /api/v1/content/2/reject; body {"reason": "Claims about odour are not supported by the source."}
- **Expected:** HTTP 200; status = "rejected"; rejection_reason = "Claims about odour are not supported by the source."
- **Actual:** HTTP 200 {"id": 2, "brief_id": 1, "campaign_id": 1, "platform": "linkedin", "status": "rejected", "created_by": "6bbd8fda-48ba-44e0-8df1-31bdbbe8a3b5", "created_at": "2026-11-24T18:35:57.779506", "updated_at": "2026-11-24T18:35:57.783419", "current_version": {"id": 2, "version_no": 1, "body": "Spring Compost Kit: what urban gardeners should know.\n\nEasy, odour-free, made from recycled material\n\nKey terms: organic, sustaina ...(truncated)

### TC-145 - Reviewer rejects a piece with a reason; the creator can read it  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US8
- **Input:** as Bob Creator (bob); path /api/v1/content/2
- **Expected:** HTTP 200; status = "rejected"; rejection_reason = "Claims about odour are not supported by the source."
- **Actual:** HTTP 200 {"id": 2, "brief_id": 1, "campaign_id": 1, "platform": "linkedin", "status": "rejected", "created_by": "6bbd8fda-48ba-44e0-8df1-31bdbbe8a3b5", "created_at": "2026-11-24T18:35:57.779506", "updated_at": "2026-11-24T18:35:57.783419", "current_version": {"id": 2, "version_no": 1, "body": "Spring Compost Kit: what urban gardeners should know.\n\nEasy, odour-free, made from recycled material\n\nKey terms: organic, sustaina ...(truncated)

### TC-146 - Rejection without a reason is refused  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/reject`  |  **User story:** US8
- **Input:** as Carol Reviewer (carol); path /api/v1/content/2/reject; body {}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "reason"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "reason", "message": "Field required"}]}

### TC-147 - A reason shorter than 10 characters is refused  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/reject`  |  **User story:** US8
- **Input:** as Carol Reviewer (carol); path /api/v1/content/2/reject; body {"reason": "too short"}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "reason"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "reason", "message": "String should have at least 10 characters"}]}

### TC-148 - Creators cannot reject  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/reject`  |  **User story:** US8
- **Input:** as Bob Creator (bob); path /api/v1/content/2/reject; body {"reason": "I do not like this one."}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: reviewer.", "code": "FORBIDDEN"}

### TC-149 - A rejected piece cannot be approved afterwards  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US8
- **Input:** as Frank Reviewer (frank); path /api/v1/content/2/approve
- **Expected:** HTTP 409; code = "INVALID_STATE"; detail = "Rejected content is final."
- **Actual:** HTTP 409 {"detail": "Rejected content is final.", "code": "INVALID_STATE"}

### TC-150 - A rejected piece cannot be edited  `PASS`
- **API:** `PATCH /api/v1/content/{piece_id}`  |  **User story:** US8
- **Input:** as Bob Creator (bob); path /api/v1/content/2; body {"body": "fixed"}
- **Expected:** HTTP 409; code = "INVALID_STATE"
- **Actual:** HTTP 409 {"detail": "Rejected content is final and cannot be edited.", "code": "INVALID_STATE"}

### TC-151 - A rejected piece cannot be regenerated  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US8
- **Input:** as Frank Reviewer (frank); path /api/v1/content/2/request-changes; body {"feedback": "try again please"}
- **Expected:** HTTP 409; code = "INVALID_STATE"
- **Actual:** HTTP 409 {"detail": "Rejected content is final.", "code": "INVALID_STATE"}

### TC-152 - Rejected content is kept, with its version and review  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US8
- **Input:** as Bob Creator (bob); path /api/v1/content/2
- **Expected:** HTTP 200; versions.0.version_no = 1; reviews.0.decision = "rejected"
- **Actual:** HTTP 200 {"id": 2, "brief_id": 1, "campaign_id": 1, "platform": "linkedin", "status": "rejected", "created_by": "bf205e1e-bfd9-4638-af4e-e5461e77a141", "created_at": "2026-11-24T18:35:58.076429", "updated_at": "2026-11-24T18:35:58.080260", "current_version": {"id": 2, "version_no": 1, "body": "Spring Compost Kit: what urban gardeners should know.\n\nEasy, odour-free, made from recycled material\n\nKey terms: organic, sustaina ...(truncated)

### TC-153 - Request changes yields one revised version and returns the piece to pending review  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3/request-changes; body {"feedback": "Make the call to action stronger."}
- **Expected:** HTTP 200; status = "pending_review"; current_version.version_no = 2; current_version.origin = "regeneration"; current_version.body = contains 'stronger'
- **Actual:** HTTP 200 {"id": 3, "brief_id": 1, "campaign_id": 1, "platform": "facebook", "status": "pending_review", "created_by": "252895d2-077e-4459-bd30-0e84ea70b710", "created_at": "2026-11-24T18:35:58.120151", "updated_at": "2026-11-24T18:35:58.124557", "current_version": {"id": 5, "version_no": 2, "body": "Spring Compost Kit - Easy, odour-free, made from recycled material Key terms: organic, sustainable.\n\nLearn more today!\n\n[Rev ...(truncated)

### TC-154 - Version 1 and the feedback review are kept  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US9
- **Input:** as Bob Creator (bob); path /api/v1/content/3
- **Expected:** HTTP 200; versions.0.version_no = 1; versions.1.version_no = 2; reviews.0.decision = "changes_requested"; reviews.0.feedback = "Make the call to action stronger."
- **Actual:** HTTP 200 {"id": 3, "brief_id": 1, "campaign_id": 1, "platform": "facebook", "status": "pending_review", "created_by": "ab1688a5-eec5-42df-81c8-3481dcdf322d", "created_at": "2026-11-24T18:35:58.162571", "updated_at": "2026-11-24T18:35:58.166856", "current_version": {"id": 5, "version_no": 2, "body": "Spring Compost Kit - Easy, odour-free, made from recycled material Key terms: organic, sustainable.\n\nLearn more today!\n\n[Rev ...(truncated)

### TC-155 - two versions exist  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`
- **Input:** -
- **Expected:** 2
- **Actual:** 2

### TC-156 - Other pieces of the same brief stay on version 1  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/1
- **Expected:** HTTP 200; current_version.version_no = 1; status = "pending_review"
- **Actual:** HTTP 200 {"id": 1, "brief_id": 1, "campaign_id": 1, "platform": "blog", "status": "pending_review", "created_by": "3148aed5-3b07-4cf6-bb4f-51df65704868", "created_at": "2026-11-24T18:35:58.206632", "updated_at": "2026-11-24T18:35:58.206972", "current_version": {"id": 1, "version_no": 1, "body": "# Spring Compost Kit\n\nIntro: Drive pre-orders of the compost kit\n\n## Why it matters for urban gardeners\nEasy, odour-free, made  ...(truncated)

### TC-157 - Request changes without feedback is refused  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3/request-changes; body {}
- **Expected:** HTTP 422; code = "VALIDATION_ERROR"; errors.0.field = "feedback"
- **Actual:** HTTP 422 {"detail": "Validation failed.", "code": "VALIDATION_ERROR", "errors": [{"field": "feedback", "message": "Field required"}]}

### TC-158 - Creators cannot request changes (reviewer action)  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US9
- **Input:** as Bob Creator (bob); path /api/v1/content/3/request-changes; body {"feedback": "Make it shorter please"}
- **Expected:** HTTP 403; code = "FORBIDDEN"
- **Actual:** HTTP 403 {"detail": "This action requires one of these campaign roles: reviewer.", "code": "FORBIDDEN"}

### TC-159 - AI failure on regeneration returns 502 and leaves the piece untouched  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3/request-changes; body {"feedback": "Make the call to action stronger."}
- **Expected:** HTTP 502; code = "GENERATION_FAILED"
- **Actual:** HTTP 502 {"detail": "The AI provider failed; no changes were saved. (simulated provider outage)", "code": "GENERATION_FAILED"}

### TC-160 - AI failure on regeneration returns 502 and leaves the piece untouched  `PASS`
- **API:** `GET /api/v1/content/{piece_id}`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3
- **Expected:** HTTP 200; status = "pending_review"; current_version.version_no = 1; reviews = []
- **Actual:** HTTP 200 {"id": 3, "brief_id": 1, "campaign_id": 1, "platform": "facebook", "status": "pending_review", "created_by": "3552ae16-f63c-4221-9cdb-625b07c5e84e", "created_at": "2026-11-24T18:35:58.332692", "updated_at": "2026-11-24T18:35:58.332932", "current_version": {"id": 3, "version_no": 1, "body": "Spring Compost Kit - Easy, odour-free, made from recycled material Key terms: organic, sustainable.\n\nLearn more today!", "crea ...(truncated)

### TC-161 - Feedback on an outdated version is refused  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/request-changes`  |  **User story:** US9
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3/request-changes; body {"feedback": "Stronger CTA please.", "version_no": 1}
- **Expected:** HTTP 409; code = "STALE_VERSION"
- **Actual:** HTTP 409 {"detail": "You reviewed version 1, but the current version is 2.", "code": "STALE_VERSION"}

### TC-162 - Request changes, then approve the revised version  `PASS`
- **API:** `POST /api/v1/content/{piece_id}/approve`  |  **User story:** US9, US7
- **Input:** as Carol Reviewer (carol); path /api/v1/content/3/approve; body {"version_no": 2}
- **Expected:** HTTP 200; status = "approved"; current_version.version_no = 2
- **Actual:** HTTP 200 {"id": 3, "brief_id": 1, "campaign_id": 1, "platform": "facebook", "status": "approved", "created_by": "b720d5ca-f228-4092-95be-fdcff77af388", "created_at": "2026-11-24T18:35:58.418839", "updated_at": "2026-11-24T18:35:58.426327", "current_version": {"id": 5, "version_no": 2, "body": "Spring Compost Kit - Easy, odour-free, made from recycled material Key terms: organic, sustainable.\n\nLearn more today!\n\n[Revised a ...(truncated)
