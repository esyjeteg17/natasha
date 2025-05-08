<script setup lang="ts">
const authStore = useAuthStore()
const router = useRouter()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const fullName = computed(() =>
	authStore.user
		? `${authStore.user.first_name} ${authStore.user.last_name}`
		: ''
)

function logout() {
	authStore.logout()
	router.push({ name: 'index' })
}

// Search
const searchQuery = ref('')
const suggestions = ref<Array<{ id: number; title: string }>>([])
let debounceTimer: ReturnType<typeof setTimeout> | null = null

watch(searchQuery, val => {
	if (debounceTimer) clearTimeout(debounceTimer)
	if (!val || val.length < 2) {
		suggestions.value = []
		return
	}
	debounceTimer = setTimeout(fetchCourses, 300)
})

async function fetchCourses() {
	try {
		const data = await $fetch('/api/courses/', {
			baseURL: authStore.baseURL,
			params: { search: searchQuery.value, ordering: 'title' },
			headers: { Authorization: `Bearer ${authStore.accessToken}` },
		})
		suggestions.value = data
			? data.map((c: any) => ({ id: c.id, title: c.title }))
			: []
	} catch (e) {
		console.error('Search error', e)
		suggestions.value = []
	}
}
</script>

<template>
	<div class="container mx-auto py-1">
		<header class="flex items-center justify-between py-3 relative">
			<!-- Logo -->
			<NuxtLink :to="{ name: 'index' }" class="flex items-center font-bold">
				<p>Учебный портал</p>
				<img src="/img/icons/logo.svg" alt="Logo" class="ml-2" />
			</NuxtLink>

			<!-- Search -->
			<div class="relative w-[305px]">
				<input
					v-model="searchQuery"
					type="text"
					placeholder="Найти курсы"
					class="pl-12 w-full h-12 rounded-full border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
				/>
				<span
					class="absolute left-4 top-1/2 -translate-y-1/2 w-6 h-6 bg-[url('/img/icons/search_icon.svg')] bg-no-repeat bg-cover"
				></span>

				<ul
					v-if="suggestions.length"
					class="absolute z-10 mt-2 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-64 overflow-y-auto"
				>
					<li
						v-for="item in suggestions"
						:key="item.id"
						class="px-4 py-2 hover:bg-gray-100"
					>
						<NuxtLink
							:to="{ name: 'courses-id', params: { id: item.id } }"
							class="block text-gray-800"
							@click="searchQuery = ''"
						>
							{{ item.title }}
						</NuxtLink>
					</li>
				</ul>
			</div>

			<!-- Navigation -->
			<nav>
				<ul class="flex space-x-5 text-sm">
					<li><NuxtLink :to="{ name: 'my-courses' }">Дисциплины</NuxtLink></li>
					<!-- <li><NuxtLink :to="{ name: 'schedule' }">Расписание</NuxtLink></li> -->
				</ul>
			</nav>

			<!-- Auth -->
			<div>
				<div v-if="!isAuthenticated">
					<NuxtLink
						:to="{ name: 'login' }"
						class="inline-block mr-5 py-2 px-4 border border-gray-800 font-bold text-gray-800 hover:bg-gray-800 hover:text-white transition-colors"
					>
						Войти
					</NuxtLink>
					<NuxtLink
						:to="{ name: 'register' }"
						class="inline-block py-2 px-4 border border-gray-800 bg-gray-800 text-white font-bold hover:bg-white hover:text-gray-800 transition-colors"
					>
						Регистрация
					</NuxtLink>
				</div>

				<div v-else class="flex items-center space-x-4 h-full">
					<NuxtLink :to="{ name: 'profile' }" class="font-bold">
						{{ fullName }}
					</NuxtLink>
					<button
						@click="logout"
						class="inline-block py-2 px-4 border border-gray-800 font-bold text-gray-800 hover:bg-gray-800 hover:text-white transition-colors"
					>
						Выйти
					</button>
					<NuxtLink
						v-if="authStore.user?.role === 'teacher'"
						:to="{ name: 'courses-create' }"
						class="h-full p-3 flex items-center justify-center border border-gray-800 font-bold text-gray-800 hover:bg-gray-800 hover:text-white transition-colors"
					>
						<IconsPlus />
					</NuxtLink>
				</div>
			</div>
		</header>
	</div>
</template>

<style scoped>
/* При необходимости: стиль scrollbar для списка */
ul::-webkit-scrollbar {
	width: 6px;
}
</style>
