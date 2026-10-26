/**
 * Date, Time, and IPv6 Formatters
 */

export function formatDateTime(isoString) {
  if (!isoString) return '--';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  } catch (e) {
    return isoString;
  }
}

export function formatTimeAgo(isoString) {
  if (!isoString) return 'Never';
  try {
    const diff = Math.floor((new Date() - new Date(isoString)) / 1000);
    if (diff < 5) return 'Just now';
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    return `${Math.floor(diff / 3600)}h ago`;
  } catch (e) {
    return 'Recent';
  }
}

export function shortenIPv6(ipv6) {
  if (!ipv6) return '';
  if (ipv6.length <= 24) return ipv6;
  return `${ipv6.substring(0, 14)}...${ipv6.substring(ipv6.length - 8)}`;
}
