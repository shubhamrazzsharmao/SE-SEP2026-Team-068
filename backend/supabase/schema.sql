-- ContentFlow (Team 068) - Supabase / Postgres schema
-- Run once in the Supabase dashboard: SQL Editor -> New query -> paste -> Run.
--
-- Differences from the Milestone 2 ER design (see docs/schema-notes.md):
--   * users.id is a uuid that equals auth.users.id (Supabase Auth owns passwords),
--     so users.password_hash is gone.
--   * piece_comments is new (comment thread per content piece).
--   * All tables have Row Level Security enabled with NO policies. The FastAPI
--     backend connects with the database owner role (bypasses RLS) and does all
--     authorisation itself, while the public anon/authenticated keys cannot read
--     these tables through Supabase's auto-generated REST API.

-- ---------- Enums ----------
create type user_role       as enum ('user', 'admin');
create type member_role     as enum ('owner', 'creator', 'reviewer', 'brand_manager');
create type brief_status    as enum ('draft', 'generating', 'generated');
create type source_kind     as enum ('pasted_text', 'pdf', 'txt');
create type platform_type   as enum ('blog', 'linkedin', 'facebook', 'instagram');
create type job_status      as enum ('queued', 'running', 'done', 'failed');
create type content_status  as enum ('draft', 'pending_review', 'approved', 'rejected');
create type version_origin  as enum ('ai_generated', 'human_edit', 'variation', 'regeneration');
create type review_decision as enum ('approved', 'rejected', 'changes_requested');

-- ---------- Ownership ----------
create table users (
  id         uuid primary key references auth.users (id) on delete cascade,
  name       varchar(100) not null,
  email      varchar(255) not null unique,
  role       user_role    not null default 'user',
  is_active  boolean      not null default true,
  created_at timestamptz  not null default now()
);

create table brands (
  id              serial primary key,
  owner_id        uuid         not null references users (id),
  name            varchar(150) not null,
  tone            text         not null,
  preferred_terms jsonb        not null default '[]'::jsonb,
  avoided_terms   jsonb        not null default '[]'::jsonb,
  updated_by      uuid         references users (id),
  created_at      timestamptz  not null default now(),
  updated_at      timestamptz  not null default now(),
  unique (owner_id, name)
);

create table campaigns (
  id          serial primary key,
  brand_id    integer      not null references brands (id),
  owner_id    uuid         not null references users (id),
  name        varchar(150) not null,
  description text,
  created_at  timestamptz  not null default now(),
  deleted_at  timestamptz
);

create table campaign_members (
  campaign_id integer     not null references campaigns (id),
  user_id     uuid        not null references users (id),
  member_role member_role not null,
  added_by    uuid        references users (id),
  joined_at   timestamptz not null default now(),
  primary key (campaign_id, user_id)
);
create index campaign_members_user_idx on campaign_members (user_id);

-- ---------- Content ----------
create table briefs (
  id              serial primary key,
  campaign_id     integer      not null references campaigns (id),
  created_by      uuid         not null references users (id),
  topic           varchar(255) not null,
  objective       text         not null,
  target_audience text,
  key_messages    text,
  tone            varchar(100),
  platforms       jsonb        not null,
  status          brief_status not null default 'draft',
  created_at      timestamptz  not null default now(),
  updated_at      timestamptz  not null default now(),
  check (jsonb_typeof(platforms) = 'array' and jsonb_array_length(platforms) >= 1)
);
create index briefs_campaign_idx on briefs (campaign_id);

create table source_materials (          -- API arrives in Sprint 2
  id             serial primary key,
  brief_id       integer      not null references briefs (id),
  kind           source_kind  not null,
  file_name      varchar(255),
  extracted_text text         not null,
  uploaded_by    uuid         not null references users (id),
  created_at     timestamptz  not null default now()
);

create table generation_jobs (
  id            serial primary key,
  brief_id      integer      not null references briefs (id),
  requested_by  uuid         not null references users (id),
  platform      platform_type,
  status        job_status   not null default 'queued',
  error_message text,
  feedback_note text,
  created_at    timestamptz  not null default now(),
  finished_at   timestamptz
);

create table content_pieces (
  id                 serial primary key,
  brief_id           integer        not null references briefs (id),
  campaign_id        integer        not null references campaigns (id),
  platform           platform_type  not null,
  status             content_status not null default 'pending_review',
  current_version_id integer,                       -- FK added below (circular)
  created_by         uuid           not null references users (id),
  created_at         timestamptz    not null default now(),
  updated_at         timestamptz    not null default now(),
  deleted_at         timestamptz,                   -- soft delete after confirmation
  unique (brief_id, platform)
);
create index content_pieces_campaign_status_idx on content_pieces (campaign_id, status);

create table content_versions (
  id                  serial primary key,
  piece_id            integer        not null references content_pieces (id),
  job_id              integer        references generation_jobs (id),
  version_no          integer        not null,
  body                text           not null,
  creative_suggestion text,
  origin              version_origin not null,
  prompt_used         text,
  model_name          varchar(100),
  flags               jsonb,
  created_by          uuid           references users (id),   -- null when produced by AI
  created_at          timestamptz    not null default now(),
  unique (piece_id, version_no)
);

alter table content_pieces
  add constraint content_pieces_current_version_fk
  foreign key (current_version_id) references content_versions (id);

-- ---------- Governance ----------
create table reviews (
  id          serial primary key,
  version_id  integer         not null references content_versions (id),
  reviewer_id uuid            not null references users (id),
  decision    review_decision not null,
  reason      text,           -- required (10+ chars) for rejection
  feedback    text,           -- required for changes_requested
  created_at  timestamptz     not null default now()
);
create index reviews_version_idx on reviews (version_id);

create table piece_comments (
  id         serial primary key,
  piece_id   integer     not null references content_pieces (id),
  user_id    uuid        not null references users (id),
  body       text        not null,
  created_at timestamptz not null default now()
);
create index piece_comments_piece_idx on piece_comments (piece_id, created_at);

create table activity_logs (             -- insert-only: no update/delete endpoints exist
  id          serial primary key,
  campaign_id integer     not null references campaigns (id),
  piece_id    integer     references content_pieces (id),
  user_id     uuid        not null references users (id),
  action      varchar(50) not null,
  version_no  integer,
  detail      jsonb,
  created_at  timestamptz not null default now()
);
create index activity_piece_idx    on activity_logs (piece_id, created_at);
create index activity_campaign_idx on activity_logs (campaign_id, created_at);

-- ---------- Personal ideas ----------
create table ideas (                     -- API arrives in Sprint 2
  id                 serial primary key,
  owner_id           uuid         not null references users (id),
  title              varchar(200) not null,
  notes              text,
  converted_brief_id integer      references briefs (id),
  created_at         timestamptz  not null default now()
);

-- ---------- Security: block direct access through Supabase's public REST API ----------
alter table users             enable row level security;
alter table brands            enable row level security;
alter table campaigns         enable row level security;
alter table campaign_members  enable row level security;
alter table briefs            enable row level security;
alter table source_materials  enable row level security;
alter table generation_jobs   enable row level security;
alter table content_pieces    enable row level security;
alter table content_versions  enable row level security;
alter table reviews           enable row level security;
alter table piece_comments    enable row level security;
alter table activity_logs     enable row level security;
alter table ideas             enable row level security;
