-- ============================================================================
-- Planwise Enterprise — Migration 08: Organization Membership & RBAC Mapping
-- Phase 5 Tenant Isolation & User Role Authorization
-- ============================================================================

-- 1. Organizations Table
CREATE TABLE IF NOT EXISTS public.organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(256) NOT NULL,
    slug VARCHAR(128) UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_organizations_slug ON public.organizations(slug);

-- 2. Organization Memberships Table (Linking auth.users to organizations)
CREATE TABLE IF NOT EXISTS public.organization_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES public.organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role VARCHAR(32) NOT NULL DEFAULT 'MEMBER' CHECK (role IN ('OWNER', 'ADMIN', 'MEMBER', 'VIEWER')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_org_user_membership UNIQUE (organization_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_org_memberships_user ON public.organization_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_org_memberships_org ON public.organization_memberships(organization_id);

-- 3. Security-Definer Helper Function with Fixed search_path
CREATE OR REPLACE FUNCTION public.get_user_organization_ids()
RETURNS SETOF UUID
SECURITY DEFINER
SET search_path = pg_catalog, public
LANGUAGE plpgsql STABLE AS $$
BEGIN
    RETURN QUERY
    SELECT organization_id
    FROM public.organization_memberships
    WHERE user_id = auth.uid()
    UNION
    SELECT NULLIF(current_setting('request.jwt.claims', true)::jsonb->>'org_id', '')::uuid
    WHERE NULLIF(current_setting('request.jwt.claims', true)::jsonb->>'org_id', '') IS NOT NULL;
END;
$$;

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.organization_memberships ENABLE ROW LEVEL SECURITY;

-- 5. Administrative / Service Role Full Access
CREATE POLICY "admin_all_organizations" ON public.organizations
    FOR ALL TO service_role, postgres
    USING (true) WITH CHECK (true);

CREATE POLICY "admin_all_memberships" ON public.organization_memberships
    FOR ALL TO service_role, postgres
    USING (true) WITH CHECK (true);

-- 6. Authenticated Tenant Read Access
CREATE POLICY "members_read_own_organization" ON public.organizations
    FOR SELECT TO authenticated
    USING (id IN (SELECT public.get_user_organization_ids()));

CREATE POLICY "members_read_own_memberships" ON public.organization_memberships
    FOR SELECT TO authenticated
    USING (organization_id IN (SELECT public.get_user_organization_ids()));

-- 7. Org Admin Mutation Access
CREATE POLICY "admins_manage_memberships" ON public.organization_memberships
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.organization_memberships m
            WHERE m.organization_id = organization_memberships.organization_id
              AND m.user_id = auth.uid()
              AND m.role IN ('OWNER', 'ADMIN')
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.organization_memberships m
            WHERE m.organization_id = organization_memberships.organization_id
              AND m.user_id = auth.uid()
              AND m.role IN ('OWNER', 'ADMIN')
        )
    );

-- 8. Update Projects Policies to use get_user_organization_ids()
DROP POLICY IF EXISTS "tenant_projects_select" ON projects;
DROP POLICY IF EXISTS "tenant_projects_insert" ON projects;
DROP POLICY IF EXISTS "tenant_projects_update" ON projects;

CREATE POLICY "tenant_projects_select" ON projects
    FOR SELECT TO authenticated
    USING (organization_id IN (SELECT public.get_user_organization_ids()));

CREATE POLICY "tenant_projects_insert" ON projects
    FOR INSERT TO authenticated
    WITH CHECK (organization_id IN (SELECT public.get_user_organization_ids()));

CREATE POLICY "tenant_projects_update" ON projects
    FOR UPDATE TO authenticated
    USING (organization_id IN (SELECT public.get_user_organization_ids()))
    WITH CHECK (organization_id IN (SELECT public.get_user_organization_ids()));
