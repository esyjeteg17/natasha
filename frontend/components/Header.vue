<template>
	<header class="sticky top-0 z-50 bg-white shadow-sm">
		<div class="max-w-7xl mx-auto">
			<div class="flex items-center justify-between h-16">
				<!-- Logo -->
				<NuxtLink to="/" class="flex items-center space-x-2">
					<img src="/img/icons/logo.svg" alt="Logo" class="h-8 w-8" />
					<span class="text-lg font-extrabold text-gray-900"
						>Учебный портал</span
					>
				</NuxtLink>

				<!-- Search -->
				<div class="relative w-full max-w-sm">
					<input
						v-model="searchQuery"
						type="text"
						placeholder="Найти курс..."
						class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
					/>
					<svg
						class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2 pointer-events-none"
						fill="currentColor"
						viewBox="0 0 20 20"
					>
						<path
							fill-rule="evenodd"
							d="M12.9 14.32a8 8 0 111.414-1.414l4.387 4.387a1 1 0 01-1.414 1.414l-4.387-4.387zM8 14a6 6 0 100-12 6 6 0 000 12z"
							clip-rule="evenodd"
						/>
					</svg>
					<!-- suggestions -->
					<ul
						v-if="suggestions.length"
						class="absolute z-40 mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto"
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

				<!-- Nav & Auth -->
				<div class="flex items-center space-x-6">
					<nav class="hidden md:flex space-x-4 text-gray-700">
						<NuxtLink
							to="/my-courses"
							class="hover:text-blue-600 transition"
							active-class="text-blue-600"
						>
							Дисциплины
						</NuxtLink>
						<!-- <NuxtLink to="/schedule" class="hover:text-blue-600 transition">Расписание</NuxtLink> -->
					</nav>

					<div v-if="!isAuthenticated" class="flex space-x-3">
						<NuxtLink
							to="/login"
							class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition"
						>
							Войти
						</NuxtLink>
						<NuxtLink
							to="/register"
							class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
						>
							Регистрация
						</NuxtLink>
					</div>

					<div v-else class="flex items-center space-x-4">
						<NuxtLink
							to="/profile"
							class="text-gray-800 font-medium hover:text-blue-600 transition"
						>
							{{ fullName }}
						</NuxtLink>
						<button
							@click="logout"
							class="px-3 py-1 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition"
						>
							Выйти
						</button>
						<NuxtLink
							v-if="authStore.user?.role === 'teacher'"
							to="/courses/create"
							class="p-2 bg-green-500 text-white rounded-full hover:bg-green-600 transition"
							title="Создать курс"
						>
							<IconsPlus class="w-5 h-5" />
						</NuxtLink>
					</div>
				</div>
			</div>
		</div>
	</header>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

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

// Search logic (скопируйте ваш код для searchQuery, suggestions и fetchCourses)
const searchQuery = ref('')
const suggestions = ref<{ id: number; title: string }[]>([])
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
	} catch {
		suggestions.value = []
	}
}
</script>

<style scoped>
/* Optional: кастомный скроллбар в списке подсказок */
ul::-webkit-scrollbar {
	width: 4px;
}
ul::-webkit-scrollbar-thumb {
	background-color: rgba(0, 0, 0, 0.2);
	border-radius: 2px;
}
</style>
