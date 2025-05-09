import { jwtDecode } from 'jwt-decode'
import type { UserData } from '~/types'
import Cookies from 'js-cookie'

// Тип для payload JWT
interface JWTPayload {
	exp: number
}

export const useAuthStore = defineStore('auth', () => {
	// 1. Инициализация стора без SSR-проблем: начальные токены в null
	const accessToken = ref<string | null>(null)
	const refreshToken = ref<string | null>(null)
	const user = ref<UserData | null>(null)
	const baseURL = 'https://uchebnyicourse-k-n.ru'
	let refreshTimeout: ReturnType<typeof setTimeout> | null = null

	// 2. Вычисляемые свойства
	const isAuthenticated = computed(() => !!accessToken.value)
	const isTeacher = computed(() => user.value?.role === 'teacher')
	const isStudent = computed(() => user.value?.role === 'student')

	// 3. Планируем авто-рефреш
	function scheduleTokenRefresh(token: string) {
		if (refreshTimeout) clearTimeout(refreshTimeout)
		const { exp } = jwtDecode<JWTPayload>(token)
		const msBefore = exp * 1000 - Date.now() - 60_000
		if (msBefore <= 0) {
			tryRefreshTokens().then(
				ok => ok && accessToken.value && scheduleTokenRefresh(accessToken.value)
			)
		} else {
			refreshTimeout = setTimeout(async () => {
				const ok = await tryRefreshTokens()
				if (ok && accessToken.value) scheduleTokenRefresh(accessToken.value)
			}, msBefore)
		}
	}

	// 4. Универсальный fetch с учётом токена
	const authFetch = async (endpoint: string, options: any = {}) => {
		if (!accessToken.value) throw new Error('Нет accessToken')
		options.method ??= 'GET'
		options.headers = {
			...(options.headers || {}),
			Authorization: `Bearer ${accessToken.value}`,
		}
		try {
			return await $fetch(endpoint, { baseURL, ...options })
		} catch (err: any) {
			if (err?.status === 401) {
				const ok = await tryRefreshTokens()
				if (!ok) {
					logout()
					throw new Error('Сессия истекла')
				}
				options.headers.Authorization = `Bearer ${accessToken.value}`
				return await $fetch(endpoint, { baseURL, ...options })
			}
			throw err
		}
	}

	// 5. Login
	const login = async (username: string, password: string) => {
		const data = await $fetch<{ access: string; refresh: string }>(
			'/api/token/',
			{ baseURL, method: 'POST', body: { username, password } }
		)
		accessToken.value = data.access
		refreshToken.value = data.refresh
		scheduleTokenRefresh(data.access)
		await fetchUserProfile()
	}

	// 6. Refresh токена
	async function tryRefreshTokens(): Promise<boolean> {
		if (!refreshToken.value) return false
		try {
			const data = await $fetch<{ access: string }>('/api/token/refresh/', {
				baseURL,
				method: 'POST',
				body: { refresh: refreshToken.value },
			})
			accessToken.value = data.access
			scheduleTokenRefresh(data.access)
			return true
		} catch {
			return false
		}
	}

	// 7. Fetch профиля
	async function fetchUserProfile() {
		if (!accessToken.value) return
		try {
			user.value = (await authFetch('/api/users/me/')) as UserData
		} catch {
			user.value = null
		}
	}

	// 8. Logout
	function logout() {
		accessToken.value = null
		refreshToken.value = null
		user.value = null
		if (refreshTimeout) clearTimeout(refreshTimeout)
	}

	// 9. Синхронизация токенов в cookie
	watch(accessToken, token => {
		if (token)
			Cookies.set('accessToken', token, { secure: true, sameSite: 'lax' })
		else Cookies.remove('accessToken')
	})
	watch(refreshToken, token => {
		if (token)
			Cookies.set('refreshToken', token, { secure: true, sameSite: 'lax' })
		else Cookies.remove('refreshToken')
	})

	// 10. При монтировании на клиенте восстанавливаем сессию
	onMounted(() => {
		const at = Cookies.get('accessToken')
		const rt = Cookies.get('refreshToken')
		if (at && rt) {
			accessToken.value = at
			refreshToken.value = rt
			scheduleTokenRefresh(at)
			fetchUserProfile()
		}
	})

	return {
		accessToken,
		refreshToken,
		user,
		isAuthenticated,
		isTeacher,
		isStudent,
		baseURL,
		login,
		fetchUserProfile,
		tryRefreshTokens,
		authFetch,
		logout,
	}
})
