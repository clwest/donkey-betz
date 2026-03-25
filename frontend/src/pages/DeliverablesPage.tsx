// Deliverables Page — Standalone page wrapping the DeliverablesTab component
// Provides a full-page view of all agent-produced deliverables

import { DeliverablesTab } from './workspace/tabs/DeliverablesTab'

export default function DeliverablesPage() {
  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <DeliverablesTab />
    </div>
  )
}
