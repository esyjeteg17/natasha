import type { UserData } from '~/types'

export const useAuthStore = defineStore('auth', () => {
	const accessToken = ref<string | null>(null)
	const refreshToken = ref<string | null>(null)
	const user = ref<UserData | null>(null)

	const baseURL = 'http://127.0.0.1:8000'

	const isAuthenticated = computed(() => !!accessToken.value)
	const isTeacher = computed(() => user.value?.role === 'teacher')
	const isStudent = computed(() => user.value?.role === 'student')

	const authFetch = async (endpoint: string, options: any = {}) => {
		if (!accessToken.value) {
			throw new Error('Отсутствует accessToken — нужно войти в систему.')
		}
		if (!options.method) options.method = 'GET'
		if (!options.headers) options.headers = {}
		options.headers.Authorization = `Bearer ${accessToken.value}`

		try {
			const data = await $fetch(endpoint, {
				baseURL,
				...options,
			})
			return data
		} catch (error: any) {
			if (error?.status === 401) {
				console.warn('Срок действия access-токена, пробуем обновить...')
				const refreshed = await tryRefreshTokens()
				if (!refreshed) {
					logout()
					throw new Error('Требуется повторный вход в систему')
				}
				options.headers.Authorization = `Bearer ${accessToken.value}`
				return await $fetch(endpoint, {
					baseURL,
					...options,
				})
			}
			throw error
		}
	}

	const login = async (username: string, password: string) => {
		try {
			const data = await $fetch<{ access: string; refresh: string }>(
				'/api/token/',
				{
					baseURL,
					method: 'POST',
					body: { username, password },
				}
			)
			accessToken.value = data.access
			refreshToken.value = data.refresh
			await fetchUserProfile()
		} catch (error) {
			throw new Error('Ошибка логина или неверные учетные данные')
		}
	}

	async function fetchUserProfile() {
		if (!accessToken.value) return
		try {
			const userData = await authFetch('/api/users/me/')
			user.value = userData as UserData
		} catch (error) {
			user.value = null
			console.error('Ошибка при загрузке профиля', error)
		}
	}

	async function tryRefreshTokens(): Promise<boolean> {
		if (!refreshToken.value) return false
		try {
			const data = await $fetch<{ access: string }>('/api/token/refresh/', {
				baseURL,
				method: 'POST',
				body: { refresh: refreshToken.value },
			})
			accessToken.value = data.access
			return true
		} catch (error) {
			console.error('Не удалось обновить токен', error)
			return false
		}
	}

	function logout() {
		accessToken.value = null
		refreshToken.value = null
		user.value = null
	}

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
		logout,
	}
})
