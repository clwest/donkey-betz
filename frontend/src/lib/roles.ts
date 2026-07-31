/**
 * S3052 PR 4 — Role predicate for customer-vs-operator route/UI gating.
 *
 * MVP interpretation (Rigby T1 AGREE, Chris ratifying at PR envelope):
 * `platform_role === 'reviewer'` is treated as the customer surface. All
 * other `platform_role` values (admin / sports_analyst / content_creator /
 * agent_manager / unified_user) are operator surface.
 *
 * This mirrors the existing Sidebar precedent at
 * `frontend/src/components/layout/Sidebar.tsx:343` which already special-cases
 * reviewer for the Admin menu item.
 *
 * A first-class `customer` value in `platform_role` (or a dedicated boolean
 * field) is deferred to Phase 3+ ACL work. Until then, promote a test user to
 * `platform_role='reviewer'` to exercise the customer flow.
 */

interface UserLike {
  platform_role?: string
}

export function isCustomerRole(user: UserLike | null | undefined): boolean {
  return user?.platform_role === 'reviewer'
}

export function isOperatorRole(user: UserLike | null | undefined): boolean {
  return !!user && !isCustomerRole(user)
}
