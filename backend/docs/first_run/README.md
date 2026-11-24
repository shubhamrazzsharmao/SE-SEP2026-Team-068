# Where testing improved the API (actual output differed from expected)

`test_report_before_fixes.md` / `test_cases_before_fixes.csv` are the **unedited output of the first
complete test run**. 5 cases failed there; each exposed a real defect in the API, which is now fixed
(see `../test_report.md` for the same cases passing).

| Case | API | Expected | Actual (before the fix) | Cause and fix |
|---|---|---|---|---|
| TC-093 | `PATCH /content/{id}` (edit text) | `current_version.version_no = 2`, origin `human_edit` | HTTP 200 but `"current_version": null` | The response reused a stale in-memory object whose `versions` list did not include the new row. The data was saved correctly; only the response was wrong. Fix: reload with `populate_existing`. |
| TC-094 | `PATCH /content/{id}` on an approved piece | status `pending_review`, version 2 | status right, `"current_version": null` | Same cause, same fix. |
| TC-151 | `POST /content/{id}/request-changes` | revised version 2 (`regeneration`) in the response | status right, `"current_version": null` | Same cause, same fix. |
| TC-095 | `PATCH /content/{id}` with a blank body | 422 with `errors[0].field = "body"` | 422 but `field = ""` | The validation-error formatter stripped every path element called `body`, so a field *named* `body` vanished. Fix: drop only the leading location marker. |
| TC-108 | `POST /content/{id}/comments` with a blank body | 422 with `errors[0].field = "body"` | 422 but `field = ""` | Same cause, same fix. |

A first attempt of the harness also failed for a reason in the test code (a response field named
`status` collided with a helper argument); that was a test bug, not an API defect, and is not listed.
