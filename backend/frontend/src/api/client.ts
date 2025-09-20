export async function api<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
    ...opts,
  })
  const contentType = res.headers.get('content-type') || ''
  const isJson = contentType.includes('application/json')
  const data = isJson ? await res.json() : await res.text()
  if (!res.ok) {
    const msg = isJson ? (data?.error || res.statusText) : res.statusText
    throw new Error(msg)
  }
  return data as T
}
