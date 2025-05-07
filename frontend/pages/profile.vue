<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { onMounted } from 'vue'

const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
	if (!authStore.user) {
		router.push('/login')
	}
})
</script>

<template>
	<div class="min-h-screen bg-gray-50">
		<main class="max-w-7xl mx-auto py-8">
			<div class="bg-white rounded-lg shadow-md p-8">
				<h2 class="text-2xl font-semibold mb-6">
					Информация о
					{{
						authStore.user?.role === 'student' ? 'студенте' : 'преподавателе'
					}}
				</h2>
				<div
					class="grid grid-cols-1 md:grid-cols-[250px_auto_1fr] gap-8 items-start"
				>
					<div class="w-full h-auto">
						<img
							src="/img/profile.png"
							alt="Profile"
							class="w-full h-full object-cover rounded-lg"
						/>
					</div>
					<div class="space-y-4">
						<div class="flex items-center space-x-4">
							<div
								class="bg-blue-600 text-white text-xl font-semibold w-12 h-12 flex items-center justify-center rounded"
							>
								0
							</div>
							<span class="text-gray-700">Лабораторные на проверке</span>
						</div>
						<div class="flex items-center space-x-4">
							<div
								class="bg-blue-600 text-white text-xl font-semibold w-12 h-12 flex items-center justify-center rounded"
							>
								0
							</div>
							<span class="text-gray-700">Лабораторные на проверке</span>
						</div>
						<div class="flex items-center space-x-4">
							<div
								class="bg-blue-600 text-white text-xl font-semibold w-12 h-12 flex items-center justify-center rounded"
							>
								0
							</div>
							<span class="text-gray-700">Лабораторные на проверке</span>
						</div>
					</div>
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
		</main>
	</div>
</template>

<style scoped>
/* Дополнительные стили при необходимости */
</style>
