import { ref, type Ref } from 'vue'

const BASE = '/api'

export function useApi<T>() {
  const data: Ref<T | null> = ref(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function request(url: string, options?: RequestInit): Promise<T | null> {
    loading.value = true
    error.value = null
    try {
      const token = localStorage.getItem('token')
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      }
      const res = await fetch(`${BASE}${url}`, {
        headers,
        ...options,
      })
      if (res.status === 401) {
        localStorage.removeItem('token')
        window.location.href = '/login'
        return null
      }
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail || `请求失败 (${res.status})`)
      }
      const json = await res.json()
      data.value = json
      return json
    } catch (e) {
      error.value = (e as Error).message
      return null
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, request }
}
