-- TALLENTIN Vocabulary Engine V2.4 complete schema
-- Apply this before running scripts/load_supabase_all.py

create table if not exists vocab_terms (
  term_id text primary key,
  preferred_term text not null unique,
  display_label text not null,
  dimension text not null,
  parent_term text,
  definition text not null,
  simple_definition text,
  includes jsonb default '[]'::jsonb,
  excludes jsonb default '[]'::jsonb,
  evidence_status text not null,
  maturity_status text not null,
  bias_status text not null,
  regulated_flag text not null,
  source_confidence_score int not null check (source_confidence_score between 1 and 5),
  country_notes jsonb default '{}'::jsonb,
  routing_use text,
  problem_solved text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists vocab_aliases (
  alias_id bigserial primary key,
  alias text not null,
  preferred_term text not null,
  alias_type text not null,
  country_scope text default 'all',
  source text,
  confidence int check (confidence between 1 and 5),
  unique(alias, preferred_term)
);

create table if not exists vocab_roles (
  role_id bigserial primary key,
  role_title text not null,
  role_family text,
  mapped_term text not null,
  mapped_dimension text,
  country_scope text default 'Canada/India/USA',
  source text,
  confidence int check (confidence between 1 and 5)
);

create table if not exists vocab_skills (
  skill_id bigserial primary key,
  skill_name text not null,
  skill_cluster text,
  mapped_term text not null,
  mapped_dimension text,
  skill_type text,
  country_scope text default 'all',
  evidence_status text,
  confidence int check (confidence between 1 and 5)
);

create table if not exists vocab_relationships (
  relationship_id bigserial primary key,
  from_term text not null,
  relationship text not null,
  to_term text not null,
  reason text,
  source text,
  confidence int check (confidence between 1 and 5)
);

create table if not exists vocab_sources (
  source_id bigserial primary key,
  source_name text not null,
  category text not null,
  allowed_use text not null,
  url text,
  risk text,
  last_reviewed date
);

create table if not exists vocab_review_queue (
  review_id bigserial primary key,
  submitted_term text not null,
  suspected_dimension text,
  reason text,
  priority text default 'medium',
  status text default 'pending',
  reviewer text,
  decision_notes text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists idx_vocab_terms_preferred_term on vocab_terms(preferred_term);
create index if not exists idx_vocab_terms_dimension on vocab_terms(dimension);
create index if not exists idx_vocab_aliases_alias on vocab_aliases(alias);
create index if not exists idx_vocab_roles_title on vocab_roles(role_title);
create index if not exists idx_vocab_skills_name on vocab_skills(skill_name);

-- Required runtime order:
-- blocked check -> alias normalization -> preferred term lookup -> country/context gate -> maturity/bias gate -> routing.
