/**
 * PrivacyGuard IPv6 - Application Constants
 */

export const TENANTS = [
  { id: 'tenant-alpha', name: 'Tenant Alpha (Smart Facility A)', prefix: '2001:db8:1::/64' },
  { id: 'tenant-beta', name: 'Tenant Beta (Smart Logistics B)', prefix: '2001:db8:2::/64' }
];

export const SEVERITY_COLORS = {
  CRITICAL: {
    bg: 'bg-red-500/10',
    border: 'border-red-500/30',
    text: 'text-red-400',
    badge: 'bg-red-500/20 text-red-300 border-red-500/40',
    dot: 'bg-red-500'
  },
  HIGH: {
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/30',
    text: 'text-orange-400',
    badge: 'bg-orange-500/20 text-orange-300 border-orange-500/40',
    dot: 'bg-orange-500'
  },
  MEDIUM: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    text: 'text-amber-400',
    badge: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
    dot: 'bg-amber-500'
  },
  LOW: {
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/30',
    text: 'text-blue-400',
    badge: 'bg-blue-500/20 text-blue-300 border-blue-500/40',
    dot: 'bg-blue-400'
  },
  INFORMATIONAL: {
    bg: 'bg-slate-500/10',
    border: 'border-slate-500/30',
    text: 'text-slate-400',
    badge: 'bg-slate-500/20 text-slate-300 border-slate-500/40',
    dot: 'bg-slate-400'
  }
};

export const EVENT_TYPE_LABELS = {
  ROUTER_ADVERTISEMENT: 'Router Advertisement',
  NORMAL_RA: 'Normal RA (Authorised)',
  ROGUE_RA: 'Rogue RA (Unauthorised)',
  NEIGHBOR_SOLICITATION: 'Neighbor Solicitation',
  NEIGHBOR_ADVERTISEMENT: 'Neighbor Advertisement',
  NDP_MESSAGE: 'NDP Standard Frame',
  NDP_RATE_ANOMALY: 'NDP Rate Flood',
  IPV6_ADDRESS_ROTATED: 'SLAAC Address Rotation',
  DEVICE_CONNECTED: 'Device Connected',
  DEVICE_DISCONNECTED: 'Device Disconnected',
  PSEUDONYM_EXPIRED: 'Pseudonym Expired',
  SESSION_EXPIRED: 'Session Expired'
};
