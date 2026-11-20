"""Services: business rules, permission checks and database access, one module per domain.

Controllers call services; services use models (app.models) and never touch HTTP.
  access               who may do what in a campaign (404 for outsiders, 403 for wrong role)
  user_service         profile rows for Supabase users
  brand_service        brands (clients) and their guidelines
  campaign_service     campaigns and members
  brief_service        briefs
  generation_service   brief -> AI-generated content pieces (all-or-nothing)
  content_service      pieces, versions, edits, deletion, comments
  review_service       approve / reject / request changes (the review state machine)
  activity_service     audit trail
  dashboard_service    status counts, database health
"""
