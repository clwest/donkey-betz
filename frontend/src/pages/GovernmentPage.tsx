import { useState, useRef, useCallback, useMemo } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  Landmark,
  FileText,
  MessageSquare,
  Loader2,
  Search,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  Send,
  Users,
  Building2,
  Tag,
  User,
  MapPin,
  Vote,
  ArrowLeft,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { governmentApi, assistantApi, type GovernmentBill, type GovernmentMember } from '@/lib/api'
import { ChatMarkdown } from '@/components/ChatMarkdown'

// US States for the picker
const US_STATES = [
  { code: 'AL', name: 'Alabama' }, { code: 'AK', name: 'Alaska' }, { code: 'AZ', name: 'Arizona' },
  { code: 'AR', name: 'Arkansas' }, { code: 'CA', name: 'California' }, { code: 'CO', name: 'Colorado' },
  { code: 'CT', name: 'Connecticut' }, { code: 'DE', name: 'Delaware' }, { code: 'FL', name: 'Florida' },
  { code: 'GA', name: 'Georgia' }, { code: 'HI', name: 'Hawaii' }, { code: 'ID', name: 'Idaho' },
  { code: 'IL', name: 'Illinois' }, { code: 'IN', name: 'Indiana' }, { code: 'IA', name: 'Iowa' },
  { code: 'KS', name: 'Kansas' }, { code: 'KY', name: 'Kentucky' }, { code: 'LA', name: 'Louisiana' },
  { code: 'ME', name: 'Maine' }, { code: 'MD', name: 'Maryland' }, { code: 'MA', name: 'Massachusetts' },
  { code: 'MI', name: 'Michigan' }, { code: 'MN', name: 'Minnesota' }, { code: 'MS', name: 'Mississippi' },
  { code: 'MO', name: 'Missouri' }, { code: 'MT', name: 'Montana' }, { code: 'NE', name: 'Nebraska' },
  { code: 'NV', name: 'Nevada' }, { code: 'NH', name: 'New Hampshire' }, { code: 'NJ', name: 'New Jersey' },
  { code: 'NM', name: 'New Mexico' }, { code: 'NY', name: 'New York' }, { code: 'NC', name: 'North Carolina' },
  { code: 'ND', name: 'North Dakota' }, { code: 'OH', name: 'Ohio' }, { code: 'OK', name: 'Oklahoma' },
  { code: 'OR', name: 'Oregon' }, { code: 'PA', name: 'Pennsylvania' }, { code: 'RI', name: 'Rhode Island' },
  { code: 'SC', name: 'South Carolina' }, { code: 'SD', name: 'South Dakota' }, { code: 'TN', name: 'Tennessee' },
  { code: 'TX', name: 'Texas' }, { code: 'UT', name: 'Utah' }, { code: 'VT', name: 'Vermont' },
  { code: 'VA', name: 'Virginia' }, { code: 'WA', name: 'Washington' }, { code: 'WV', name: 'West Virginia' },
  { code: 'WI', name: 'Wisconsin' }, { code: 'WY', name: 'Wyoming' }, { code: 'DC', name: 'District of Columbia' },
]

type SubTab = 'members' | 'bills' | 'ask'
const subTabs: Array<{ id: SubTab; label: string; icon: typeof Landmark }> = [
  { id: 'members', label: 'My Reps', icon: Users },
  { id: 'bills', label: 'Bills', icon: FileText },
  { id: 'ask', label: 'Ask', icon: MessageSquare },
]

export default function GovernmentPage() {
  const [activeTab, setActiveTab] = useState<SubTab>('members')
  const [selectedMember, setSelectedMember] = useState<string | null>(null)
  const [selectedBill, setSelectedBill] = useState<string | null>(null)
  const [askContext, setAskContext] = useState<{ type: 'bill' | 'member'; id: string; label: string } | null>(null)

  // Hub stats for header
  const { data: hub } = useQuery({
    queryKey: ['government-hub'],
    queryFn: async () => (await governmentApi.hub()).data,
    staleTime: 60_000,
  })

  const handleAskAboutBill = (bill: GovernmentBill) => {
    setAskContext({ type: 'bill', id: bill.bill_uid, label: `${bill.bill_number}: ${bill.short_title || bill.title}`.slice(0, 80) })
    setActiveTab('ask')
  }

  const handleAskAboutMember = (member: GovernmentMember) => {
    setAskContext({ type: 'member', id: member.bioguide_id, label: member.full_name })
    setActiveTab('ask')
  }

  return (
    <div className="space-y-4 p-6">
      {/* Header with stats */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Landmark size={24} className="text-primary-400" />
          <h1 className="text-2xl font-bold text-white">Government & Legislation</h1>
        </div>
        {hub?.stats && (
          <div className="hidden md:flex gap-4 text-sm text-gray-400">
            <span>{hub.stats.members_count} Members</span>
            <span>{hub.stats.total_bills} Bills</span>
          </div>
        )}
      </div>

      <p className="text-gray-400 text-sm">
        Find your representatives, see what they're actually voting for, and understand how bills affect you.
      </p>

      {/* Sub-tab Navigation */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {subTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => { setActiveTab(tab.id); setSelectedMember(null); setSelectedBill(null) }}
            className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
              activeTab === tab.id
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'members' && (
        selectedMember
          ? <MemberDetail bioguideId={selectedMember} onBack={() => setSelectedMember(null)} onAsk={handleAskAboutMember} onViewBill={(uid) => { setSelectedBill(uid); setActiveTab('bills') }} />
          : <MembersTab onSelect={setSelectedMember} />
      )}
      {activeTab === 'bills' && (
        selectedBill
          ? <BillDetail billUid={selectedBill} onBack={() => setSelectedBill(null)} onAsk={handleAskAboutBill} onViewMember={(id) => { setSelectedMember(id); setActiveTab('members') }} />
          : <BillsTab onSelect={setSelectedBill} onAsk={handleAskAboutBill} />
      )}
      {activeTab === 'ask' && <AskTab context={askContext} onClearContext={() => setAskContext(null)} />}
    </div>
  )
}

// =============================================================================
// Members Tab — State → Chamber → District picker
// =============================================================================

function MembersTab({ onSelect }: { onSelect: (id: string) => void }) {
  const [state, setState] = useState('')
  const [chamber, setChamber] = useState<'all' | 'house' | 'senate'>('all')
  const [district, setDistrict] = useState<string>('')

  const params: Record<string, string> = {}
  if (state) params.state = state
  if (chamber !== 'all') params.chamber = chamber
  if (district) params.district = district

  const { data, isLoading } = useQuery({
    queryKey: ['government-members', params],
    queryFn: async () => (await governmentApi.members(params)).data,
    enabled: !!state,
  })

  const { data: districtData } = useQuery({
    queryKey: ['government-districts', state],
    queryFn: async () => (await governmentApi.districts(state)).data,
    enabled: !!state && chamber !== 'senate',
  })

  const members = data?.members || []

  return (
    <div className="space-y-4">
      {/* Picker row */}
      <div className="flex flex-wrap gap-3">
        <select
          value={state}
          onChange={(e) => { setState(e.target.value); setDistrict('') }}
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500 min-w-[180px]"
        >
          <option value="">Select your state...</option>
          {US_STATES.map((s) => (
            <option key={s.code} value={s.code}>{s.name}</option>
          ))}
        </select>

        {state && (
          <select
            value={chamber}
            onChange={(e) => { setChamber(e.target.value as 'all' | 'house' | 'senate'); setDistrict('') }}
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
          >
            <option value="all">All Chambers</option>
            <option value="house">House</option>
            <option value="senate">Senate</option>
          </select>
        )}

        {state && chamber !== 'senate' && districtData?.districts && districtData.districts.length > 0 && (
          <select
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
            className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
          >
            <option value="">All Districts</option>
            {districtData.districts.map((d) => (
              <option key={d} value={d}>District {d}</option>
            ))}
          </select>
        )}
      </div>

      {!state && (
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-8 text-center">
          <MapPin size={32} className="text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400">Select your state to find your representatives</p>
          <p className="text-gray-500 text-sm mt-1">We track all 535 members of the 119th Congress</p>
        </div>
      )}

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="animate-spin text-primary-400" size={28} />
        </div>
      )}

      {state && !isLoading && members.length === 0 && (
        <div className="bg-gray-800/50 rounded-lg p-6 text-gray-400 text-center">
          No members found for this selection.
        </div>
      )}

      {/* Member cards grid */}
      {members.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {members.map((m) => (
            <MemberCard key={m.bioguide_id} member={m} onClick={() => onSelect(m.bioguide_id)} />
          ))}
        </div>
      )}
    </div>
  )
}

function MemberCard({ member, onClick }: { member: GovernmentMember; onClick: () => void }) {
  const partyColor = member.party.startsWith('Democrat')
    ? 'border-blue-500/40 bg-blue-500/5'
    : member.party.startsWith('Republican')
    ? 'border-red-500/40 bg-red-500/5'
    : 'border-gray-600/40 bg-gray-800/50'

  const partyBadgeColor = member.party.startsWith('Democrat')
    ? 'bg-blue-500/20 text-blue-400'
    : member.party.startsWith('Republican')
    ? 'bg-red-500/20 text-red-400'
    : 'bg-gray-600/20 text-gray-400'

  return (
    <button
      onClick={onClick}
      className={cn('border rounded-lg p-4 text-left hover:bg-gray-800/80 transition-colors w-full', partyColor)}
    >
      <div className="flex items-start gap-3">
        {member.photo_url ? (
          <img
            src={member.photo_url}
            alt={member.full_name}
            className="w-14 h-14 rounded-full object-cover border-2 border-gray-600"
          />
        ) : (
          <div className="w-14 h-14 rounded-full bg-gray-700 flex items-center justify-center">
            <User size={24} className="text-gray-500" />
          </div>
        )}
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-white truncate">{member.full_name}</p>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span className={cn('px-2 py-0.5 rounded text-xs', partyBadgeColor)}>
              {member.party.charAt(0)}
            </span>
            <span className="text-xs text-gray-400">
              {member.chamber === 'senate' ? 'Senator' : 'Rep.'} — {member.state}
              {member.district != null ? `-${member.district}` : ''}
            </span>
          </div>
          {member.leadership_role && (
            <p className="text-xs text-yellow-400 mt-1 truncate">{member.leadership_role}</p>
          )}
        </div>
      </div>
    </button>
  )
}

// =============================================================================
// Member Detail
// =============================================================================

function MemberDetail({
  bioguideId,
  onBack,
  onAsk,
  onViewBill,
}: {
  bioguideId: string
  onBack: () => void
  onAsk: (m: GovernmentMember) => void
  onViewBill: (uid: string) => void
}) {
  const { data: member, isLoading } = useQuery({
    queryKey: ['government-member', bioguideId],
    queryFn: async () => (await governmentApi.memberDetail(bioguideId)).data,
  })

  if (isLoading || !member) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-primary-400" size={28} />
      </div>
    )
  }

  const partyColor = member.party.startsWith('Democrat') ? 'text-blue-400' : member.party.startsWith('Republican') ? 'text-red-400' : 'text-gray-400'

  return (
    <div className="space-y-6">
      <button onClick={onBack} className="flex items-center gap-1 text-sm text-gray-400 hover:text-white">
        <ArrowLeft size={14} /> Back to members
      </button>

      {/* Header */}
      <div className="flex items-start gap-4">
        {member.photo_url ? (
          <img src={member.photo_url} alt={member.full_name} className="w-20 h-20 rounded-full object-cover border-2 border-gray-600" />
        ) : (
          <div className="w-20 h-20 rounded-full bg-gray-700 flex items-center justify-center">
            <User size={32} className="text-gray-500" />
          </div>
        )}
        <div>
          <h2 className="text-xl font-bold text-white">{member.full_name}</h2>
          <p className={cn('text-sm', partyColor)}>{member.party}</p>
          <p className="text-sm text-gray-400">
            {member.chamber === 'senate' ? 'Senator' : 'Representative'} — {member.state}
            {member.district != null ? `, District ${member.district}` : ''}
          </p>
          {member.leadership_role && <p className="text-xs text-yellow-400 mt-1">{member.leadership_role}</p>}
          <button
            onClick={() => onAsk(member)}
            className="mt-2 px-3 py-1.5 bg-primary-600/20 border border-primary-500/30 rounded text-primary-400 text-xs hover:bg-primary-600/30 transition-colors"
          >
            Ask about this member
          </button>
        </div>
      </div>

      {/* Voting Record */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
          <Vote size={18} /> Voting Record
          {member.vote_count != null && <span className="text-sm text-gray-400 font-normal">({member.vote_count} votes)</span>}
        </h3>
        {member.votes && member.votes.length > 0 ? (
          <div className="space-y-2">
            {member.votes.map((v, i) => (
              <div key={i} className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-3 flex items-center gap-3">
                <span className={cn(
                  'px-2 py-1 rounded text-xs font-semibold min-w-[50px] text-center',
                  v.position === 'Yea' ? 'bg-green-500/20 text-green-400' :
                  v.position === 'Nay' ? 'bg-red-500/20 text-red-400' :
                  'bg-gray-600/20 text-gray-400'
                )}>
                  {v.position}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-200 truncate">
                    {v.bill_title || v.question}
                  </p>
                  <p className="text-xs text-gray-500">
                    {v.date} — {v.result}
                  </p>
                </div>
                {v.bill_uid && (
                  <button
                    onClick={() => onViewBill(v.bill_uid!)}
                    className="text-xs text-primary-400 hover:text-primary-300 whitespace-nowrap"
                  >
                    View Bill
                  </button>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-gray-800/30 border border-gray-700/30 rounded-lg p-6 text-center text-gray-500">
            <Vote size={24} className="mx-auto mb-2 opacity-50" />
            <p>Vote data is still syncing for this member.</p>
            <p className="text-xs mt-1">Check back soon — we're pulling roll call votes from Congress.gov</p>
          </div>
        )}
      </div>

      {/* Sponsored Bills */}
      {member.sponsored_bills && member.sponsored_bills.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
            <FileText size={18} /> Sponsored Bills ({member.sponsored_bills.length})
          </h3>
          <div className="space-y-2">
            {member.sponsored_bills.map((b) => (
              <button
                key={b.bill_uid}
                onClick={() => onViewBill(b.bill_uid)}
                className="w-full text-left bg-gray-800/50 border border-gray-700/50 rounded-lg p-3 hover:bg-gray-800/80 transition-colors"
              >
                <span className="font-mono text-xs text-primary-400">{b.bill_number}</span>
                <p className="text-sm text-gray-200 line-clamp-1 mt-1">{b.short_title || b.title}</p>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// =============================================================================
// Bills Tab
// =============================================================================

function BillsTab({ onSelect, onAsk }: { onSelect: (uid: string) => void; onAsk: (bill: GovernmentBill) => void }) {
  const [search, setSearch] = useState('')
  const [chamberFilter, setChamberFilter] = useState<string>('all')
  const [page, setPage] = useState(1)

  const params: Record<string, string | number> = { page, per_page: 30 }
  if (chamberFilter !== 'all') params.chamber = chamberFilter
  if (search) params.q = search

  const { data, isLoading } = useQuery({
    queryKey: ['government-bills', params],
    queryFn: async () => (await governmentApi.bills(params)).data,
  })

  const bills = data?.bills || []
  const totalPages = data?.pages || 1

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
          <input
            type="text"
            placeholder="Search bills..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
          />
        </div>
        <select
          value={chamberFilter}
          onChange={(e) => { setChamberFilter(e.target.value); setPage(1) }}
          className="px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:outline-none focus:border-primary-500"
        >
          <option value="all">All Chambers</option>
          <option value="house">House</option>
          <option value="senate">Senate</option>
        </select>
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="animate-spin text-primary-400" size={28} />
        </div>
      ) : bills.length === 0 ? (
        <div className="bg-gray-800/50 rounded-lg p-6 text-gray-400 text-center">
          {search ? 'No bills match your search.' : 'No bills found. Data may still be syncing.'}
        </div>
      ) : (
        <div className="space-y-3">
          <p className="text-sm text-gray-400">{data?.total || 0} bills found</p>
          {bills.map((bill) => (
            <BillCard key={bill.bill_uid} bill={bill} onClick={() => onSelect(bill.bill_uid)} onAsk={() => onAsk(bill)} />
          ))}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-sm text-gray-300 disabled:opacity-30"
              >
                Previous
              </button>
              <span className="text-sm text-gray-400">Page {page} of {totalPages}</span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-sm text-gray-300 disabled:opacity-30"
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function BillCard({ bill, onClick, onAsk }: { bill: GovernmentBill; onClick: () => void; onAsk: () => void }) {
  const chamberColor = bill.chamber === 'senate'
    ? 'bg-blue-500/20 text-blue-400 border-blue-500/30'
    : 'bg-green-500/20 text-green-400 border-green-500/30'

  return (
    <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4 hover:bg-gray-800/80 transition-colors">
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0 cursor-pointer" onClick={onClick}>
          <div className="flex items-center gap-2 flex-wrap mb-1">
            <span className="font-mono font-semibold text-white text-sm">{bill.bill_number}</span>
            <span className={cn('px-2 py-0.5 rounded text-xs border', chamberColor)}>
              {bill.chamber === 'senate' ? 'Senate' : 'House'}
            </span>
            {bill.status && (
              <span className="px-2 py-0.5 rounded text-xs bg-gray-700/50 text-gray-300 border border-gray-600/50">
                {bill.status}
              </span>
            )}
          </div>
          <p className="text-gray-200 text-sm line-clamp-2">{bill.short_title || bill.title}</p>
          {bill.sponsor_names.length > 0 && (
            <p className="text-xs text-gray-500 mt-1">
              Sponsor: {bill.sponsor_names[0]?.name}
              {bill.sponsor_names[0]?.party ? ` (${bill.sponsor_names[0].party.charAt(0)})` : ''}
              {bill.sponsor_names.length > 1 && ` +${bill.sponsor_names.length - 1}`}
            </p>
          )}
          {bill.last_action && (
            <p className="text-xs text-gray-500 mt-1 truncate">
              Latest: {bill.last_action}
              {bill.last_action_date && ` (${bill.last_action_date})`}
            </p>
          )}
        </div>
        <button
          onClick={(e) => { e.stopPropagation(); onAsk() }}
          className="text-xs text-primary-400 hover:text-primary-300 px-2 py-1 rounded bg-primary-600/10 hover:bg-primary-600/20 whitespace-nowrap"
        >
          Ask
        </button>
      </div>
    </div>
  )
}

// =============================================================================
// Bill Detail
// =============================================================================

function BillDetail({
  billUid,
  onBack,
  onAsk,
  onViewMember,
}: {
  billUid: string
  onBack: () => void
  onAsk: (bill: GovernmentBill) => void
  onViewMember: (id: string) => void
}) {
  const { data: bill, isLoading } = useQuery({
    queryKey: ['government-bill', billUid],
    queryFn: async () => (await governmentApi.billDetail(billUid)).data,
  })

  if (isLoading || !bill) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="animate-spin text-primary-400" size={28} />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <button onClick={onBack} className="flex items-center gap-1 text-sm text-gray-400 hover:text-white">
        <ArrowLeft size={14} /> Back to bills
      </button>

      {/* Header */}
      <div>
        <div className="flex items-center gap-2 flex-wrap mb-2">
          <span className="font-mono text-lg font-bold text-white">{bill.bill_number}</span>
          <span className={cn(
            'px-2 py-0.5 rounded text-xs border',
            bill.chamber === 'senate' ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' : 'bg-green-500/20 text-green-400 border-green-500/30'
          )}>
            {bill.chamber === 'senate' ? 'Senate' : 'House'}
          </span>
          {bill.status && <span className="px-2 py-0.5 rounded text-xs bg-gray-700/50 text-gray-300">{bill.status}</span>}
        </div>
        <h2 className="text-lg text-white">{bill.title}</h2>
        {bill.introduced_date && <p className="text-sm text-gray-500 mt-1">Introduced {bill.introduced_date}</p>}
        <div className="flex gap-2 mt-3">
          <button
            onClick={() => onAsk(bill)}
            className="px-3 py-1.5 bg-primary-600/20 border border-primary-500/30 rounded text-primary-400 text-xs hover:bg-primary-600/30"
          >
            Ask about this bill
          </button>
          {bill.congress_gov_url && (
            <a href={bill.congress_gov_url} target="_blank" rel="noopener noreferrer"
               className="flex items-center gap-1 px-3 py-1.5 bg-gray-800 border border-gray-700 rounded text-xs text-gray-300 hover:text-white">
              <ExternalLink size={12} /> Congress.gov
            </a>
          )}
        </div>
      </div>

      {/* Summary */}
      {bill.plain_summary && (
        <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Summary</h3>
          <p className="text-sm text-gray-300 leading-relaxed">{bill.plain_summary}</p>
        </div>
      )}

      {/* Sponsors */}
      {bill.sponsors_linked && bill.sponsors_linked.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Sponsors</h3>
          <div className="flex flex-wrap gap-2">
            {bill.sponsors_linked.map((s) => (
              <button
                key={s.bioguide_id}
                onClick={() => onViewMember(s.bioguide_id)}
                className="flex items-center gap-2 px-3 py-2 bg-gray-800/50 border border-gray-700/50 rounded-lg hover:bg-gray-800 transition-colors"
              >
                {s.photo_url ? (
                  <img src={s.photo_url} alt={s.full_name} className="w-8 h-8 rounded-full object-cover" />
                ) : (
                  <User size={16} className="text-gray-500" />
                )}
                <div className="text-left">
                  <p className="text-sm text-white">{s.full_name}</p>
                  <p className="text-xs text-gray-400">{s.party.charAt(0)}-{s.state}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Topics */}
      {bill.topics && bill.topics.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Topics</h3>
          <div className="flex flex-wrap gap-1.5">
            {bill.topics.map((t) => (
              <span key={t} className="px-2 py-0.5 rounded-full bg-gray-700/50 text-gray-400 text-xs">{t}</span>
            ))}
          </div>
        </div>
      )}

      {/* Roll Calls */}
      {bill.roll_calls && bill.roll_calls.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-300 mb-2">Roll Call Votes</h3>
          <div className="space-y-2">
            {bill.roll_calls.map((rc) => (
              <div key={rc.id} className="bg-gray-800/50 border border-gray-700/50 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm text-gray-200">{rc.question}</p>
                  <span className={cn(
                    'px-2 py-0.5 rounded text-xs',
                    rc.result === 'Passed' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  )}>
                    {rc.result}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {rc.date} — Yea: {rc.yea_count} / Nay: {rc.nay_count}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Last Action */}
      {bill.last_action && (
        <p className="text-xs text-gray-500">
          Last action: {bill.last_action}
          {bill.last_action_date && ` (${bill.last_action_date})`}
        </p>
      )}

      {/* Freshness */}
      {bill.updated_at && (
        <p className="text-xs text-gray-600">Data last updated: {new Date(bill.updated_at).toLocaleDateString()}</p>
      )}
    </div>
  )
}

// =============================================================================
// Ask Tab — Chat with context routing
// =============================================================================

function AskTab({
  context,
  onClearContext,
}: {
  context: { type: 'bill' | 'member'; id: string; label: string } | null
  onClearContext: () => void
}) {
  return (
    <div className="max-w-3xl mx-auto">
      <p className="text-gray-400 text-sm mb-4">
        Ask questions about legislation in plain English. Answers are grounded in actual bill text
        — Reps can lie but the Bills won't.
      </p>
      {context && (
        <div className="flex items-center gap-2 mb-3 px-3 py-2 bg-primary-600/10 border border-primary-500/20 rounded-lg">
          <span className="text-xs text-primary-400">
            Asking about: <span className="font-semibold">{context.label}</span>
          </span>
          <button onClick={onClearContext} className="text-xs text-gray-500 hover:text-white ml-auto">Clear</button>
        </div>
      )}
      <AskABillChat fullWidth context={context} />
    </div>
  )
}

// =============================================================================
// Ask A Bill Chat
// =============================================================================

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

const SUGGESTED_QUESTIONS = [
  'What bills about AI regulation are in Congress right now?',
  'How does the latest healthcare bill affect regular people?',
  'What has my representative voted for recently?',
  'Explain the latest immigration bill in simple terms',
]

function AskABillChat({
  fullWidth = false,
  context,
}: {
  fullWidth?: boolean
  context?: { type: 'bill' | 'member'; id: string; label: string } | null
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isPolling, setIsPolling] = useState(false)
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  const addMessage = useCallback((msg: ChatMessage) => {
    setMessages((prev) => [...prev, msg])
    setTimeout(scrollToBottom, 100)
  }, [scrollToBottom])

  const sendMessage = useMutation({
    mutationFn: (message: string) => {
      // Build context-aware prompt
      let prompt = message
      if (context?.type === 'bill') {
        prompt = `[Bill context: ${context.label}] ${message}`
      } else if (context?.type === 'member') {
        prompt = `[Member context: ${context.label}] ${message}`
      }
      return assistantApi.paChat(`legislation ${prompt}`, {
        context: { source: 'government_page', context_type: context?.type, context_id: context?.id },
      })
    },
    onSuccess: (response) => {
      const taskId = response.data.task_id
      setIsPolling(true)

      pollRef.current = setInterval(async () => {
        try {
          const status = await assistantApi.paChatStatus(taskId)
          if (status.data.status === 'completed') {
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)
            addMessage({ role: 'assistant', content: status.data.content || 'No response' })
          } else if (status.data.status === 'failed') {
            if (pollRef.current) clearInterval(pollRef.current)
            pollRef.current = null
            setIsPolling(false)
            addMessage({ role: 'assistant', content: status.data.error || 'Sorry, there was an error.' })
          }
        } catch {
          if (pollRef.current) clearInterval(pollRef.current)
          pollRef.current = null
          setIsPolling(false)
          addMessage({ role: 'assistant', content: 'Sorry, there was an error. Please try again.' })
        }
      }, 1500)
    },
    onError: () => {
      addMessage({ role: 'assistant', content: 'Sorry, there was an error processing your request.' })
    },
  })

  const isBusy = sendMessage.isPending || isPolling

  const handleSend = (text?: string) => {
    const msg = text || input.trim()
    if (!msg || isBusy) return
    addMessage({ role: 'user', content: msg })
    setInput('')
    sendMessage.mutate(msg)
  }

  return (
    <div className={cn(
      'flex flex-col bg-gray-900/50 border border-gray-700/50 rounded-lg',
      fullWidth ? 'h-[700px]' : 'h-[500px]'
    )}>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
            <MessageSquare size={32} className="text-gray-600" />
            <div>
              <p className="text-gray-400 text-sm mb-1">Ask questions about legislation</p>
              <p className="text-gray-500 text-xs">Answers grounded in actual bill text</p>
            </div>
            <div className="space-y-2 w-full max-w-sm">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleSend(q)}
                  disabled={isBusy}
                  className="w-full px-3 py-2 text-left text-sm text-gray-300 bg-gray-800/50 border border-gray-700/50 rounded-lg hover:bg-gray-800 hover:text-white transition-colors disabled:opacity-50"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={cn('flex', msg.role === 'user' ? 'justify-end' : 'justify-start')}>
              <div className={cn(
                'max-w-[85%] rounded-lg px-4 py-3',
                msg.role === 'user'
                  ? 'bg-primary-600/20 border border-primary-500/30 text-gray-200'
                  : 'bg-gray-800/50 border border-gray-700/50'
              )}>
                {msg.role === 'assistant' ? <ChatMarkdown content={msg.content} /> : <p className="text-sm">{msg.content}</p>}
              </div>
            </div>
          ))
        )}
        {isBusy && (
          <div className="flex justify-start">
            <div className="bg-gray-800/50 border border-gray-700/50 rounded-lg px-4 py-3 flex items-center gap-2">
              <Loader2 size={14} className="animate-spin text-primary-400" />
              <span className="text-sm text-gray-400">Analyzing legislation...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-700/50 p-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder="Ask about any bill or representative..."
            disabled={isBusy}
            className="flex-1 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 text-sm focus:outline-none focus:border-primary-500 disabled:opacity-50"
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || isBusy}
            className="px-3 py-2 bg-primary-600 hover:bg-primary-500 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
