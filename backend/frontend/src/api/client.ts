export async function api<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(opts.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
  const res = await fetch(path, { ...opts, headers })
  const contentType = res.headers.get('content-type') || ''
  const isJson = contentType.includes('application/json')
  const data = isJson ? await res.json().catch(() => ({})) : await res.text()
  if (!res.ok) {
    const msg = isJson ? ((data as any)?.error || res.statusText) : res.statusText
    throw new Error(msg)
  }
  return data as T
}
