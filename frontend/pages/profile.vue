<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

// Redirect if not authenticated
onMounted(() => {
	if (!authStore.user) {
		router.push('/login')
	}
})

// Teacher's courses
const myCourses = ref<Array<{ id: number; title: string; hours: number }>>([])

async function loadMyCourses() {
	if (authStore.user?.role !== 'teacher') return
	try {
		const data = await $fetch('/api/courses/me/', {
			baseURL: authStore.baseURL,
			headers: { Authorization: `Bearer ${authStore.accessToken}` },
		})
		myCourses.value = data || []
	} catch (e) {
		console.error('Failed to load courses', e)
	}
}

onMounted(() => {
	loadMyCourses()
})
</script>

<template>
	<div class="min-h-screen bg-gray-50">
		<main class="max-w-7xl mx-auto py-8 px-4">
			<div class="bg-white rounded-lg shadow-md p-8 space-y-8">
				<!-- Profile Info -->
				<div>
					<h2 class="text-2xl font-semibold mb-6">
						Информация о
						{{
							authStore.user?.role === 'student' ? 'студенте' : 'преподавателе'
						}}
					</h2>
					<div
						class="grid grid-cols-1 md:grid-cols-[250px_auto_1fr] gap-8 items-start"
					>
						<!-- Avatar -->
						<div class="w-full h-auto">
							<img
								src="/img/profile.png"
								alt="Profile"
								class="w-full h-full object-cover rounded-lg"
							/>
						</div>
						<!-- Stats -->
						<!-- Contact -->
						<div class="space-y-6">
							<p class="text-gray-500">
								Адрес электронной почты:
								<a
									:href="`mailto:${authStore.user?.email}`"
									class="text-blue-600 hover:underline"
								>
									{{ authStore.user?.email }}
								</a>
							</p>
							<p class="text-gray-500">
								Номер телефона:
								<span class="text-blue-600">
									{{ authStore.user?.phone || 'Не указан' }}
								</span>
							</p>
							<p class="text-gray-500">
								Учебная группа:
								<span class="text-blue-600">
									{{ authStore.user?.group || 'Не указана' }}
								</span>
							</p>
							<button
								class="mt-4 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
							>
								Редактировать данные
							</button>
						</div>
					</div>
				</div>

				<!-- Teacher's Courses -->
				<div v-if="authStore.user?.role === 'teacher'" class="space-y-4">
					<h3 class="text-xl font-semibold text-gray-800">Мои курсы</h3>
					<div
						v-if="myCourses.length"
						class="grid grid-cols-1 md:grid-cols-2 gap-6"
					>
						<NuxtLink
							v-for="course in myCourses"
							:key="course.id"
							:to="{ name: 'courses-id', params: { id: course.id } }"
							class="block p-4 border border-gray-200 rounded-lg hover:shadow-lg transition"
						>
							<h4 class="text-lg font-medium text-gray-800">
								{{ course.title }}
							</h4>
							<p class="text-sm text-gray-500">Часы: {{ course.hours }}</p>
						</NuxtLink>
					</div>
					<p v-else class="text-gray-500">У вас пока нет созданных курсов.</p>
				</div>
			</div>
		</main>
	</div>
</template>
