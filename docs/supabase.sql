-- Fitness Coach: Tabelle für den Sync mit der eigenen Supabase-Datenbank.
-- Einmal im Supabase-Dashboard unter "SQL Editor" ausführen.
-- Die App schreibt Zeilen (k, t, v) per Upsert mit on_conflict=user_id,k und liest sie mit select=k,t,v.
-- Ohne Row-Level-Security (RLS) könnte jedes Konto in diesem Projekt alle Zeilen lesen und überschreiben.

create table if not exists public.kv (
  user_id uuid not null default auth.uid() references auth.users (id) on delete cascade,
  k text not null,          -- Speicherschlüssel, z. B. fc_diary
  t bigint not null,        -- Zeitstempel der letzten Änderung (ms)
  v text not null,          -- Inhalt als JSON-Text
  primary key (user_id, k)
);

alter table public.kv enable row level security;

drop policy if exists kv_select_own on public.kv;
drop policy if exists kv_insert_own on public.kv;
drop policy if exists kv_update_own on public.kv;
drop policy if exists kv_delete_own on public.kv;
create policy kv_select_own on public.kv for select to authenticated using ((select auth.uid()) = user_id);
create policy kv_insert_own on public.kv for insert to authenticated with check ((select auth.uid()) = user_id);
create policy kv_update_own on public.kv for update to authenticated using ((select auth.uid()) = user_id) with check ((select auth.uid()) = user_id);
create policy kv_delete_own on public.kv for delete to authenticated using ((select auth.uid()) = user_id);

-- Nicht angemeldete Aufrufe (nur Anon-Key) dürfen nichts.
revoke all on public.kv from anon;

-- Prüfen: rls muss true sein, und es müssen die vier Regeln oben erscheinen.
-- select relrowsecurity as rls from pg_class where oid = 'public.kv'::regclass;
-- select policyname, cmd, roles from pg_policies where tablename = 'kv';

-- Empfehlung: Wenn nur du die App nutzt, unter Authentication > Sign In / Providers
-- "Allow new users to sign up" ausschalten, sobald dein Konto angelegt ist.
