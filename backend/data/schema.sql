-- Run this once in the Supabase SQL editor (Project -> SQL Editor -> New query -> paste -> Run).
-- The backend talks to these tables with the SERVICE key. The browser never gets that key.

create table if not exists public.applications (
  id          text primary key,
  created_at  timestamptz not null default now(),
  status      text not null default 'pending',
  score       numeric,
  priority    text,
  decision    text,
  data        jsonb not null
);

create index if not exists applications_created_idx on public.applications (created_at desc);
create index if not exists applications_score_idx   on public.applications (score desc);

create table if not exists public.settings (
  key   text primary key,
  value jsonb not null
);

-- Row Level Security: on, with NO public policies. The anon key (used in the browser for login)
-- therefore cannot read or write these tables. The service key bypasses RLS on the server.
alter table public.applications enable row level security;
alter table public.settings     enable row level security;

-- Private bucket for uploaded pitch decks (the backend uses the service key; the bucket is not public).
insert into storage.buckets (id, name, public)
values ('decks', 'decks', false)
on conflict (id) do nothing;
