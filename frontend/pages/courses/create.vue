<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const errorMessage = ref('')
const showErrorPopup = ref(false)

function showError(text: string) {
	errorMessage.value = text
	showErrorPopup.value = true
}

function closeError() {
	showErrorPopup.value = false
}

// Form fields
const title = ref('')
const description = ref('')
const hours = ref<number | null>(null)
const imageFile = ref<File | null>(null)

// Redirect if not teacher
onMounted(() => {
	if (!authStore.isTeacher) {
		alert('У вас нет прав для создания курса')
		router.push('/')
	}
})

// Handle file input
function onFileSelected(e: Event) {
	const files = (e.target as HTMLInputElement).files
	if (files && files.length) {
		imageFile.value = files[0]
	}
}

// Submit handler
async function createCourse() {
	if (!authStore.isTeacher) {
		showError('Только преподаватель может создавать курс')
		return
	}
	if (!title.value || hours.value === null) {
		showError('Пожалуйста, заполните обязательные поля')
		return
	}

	try {
		const formData = new FormData()
		formData.append('title', title.value)
		formData.append('description', description.value)
		formData.append('hours', String(hours.value))
		if (imageFile.value) {
			formData.append('img', imageFile.value)
		}

		await $fetch('/api/courses/', {
			baseURL: authStore.baseURL,
			method: 'POST',
			body: formData,
			headers: {
				Authorization: `Bearer ${authStore.accessToken}`,
			},
		})

		alert('Курс успешно создан')
		router.push('/')
	} catch (err: any) {
		console.error('Ошибка при создании курса:', err)
		showError('Ошибка при создании курса: не введены данные')
	}
}
</script>

<template>
	<div class="min-h-screen bg-gray-50">
		<main class="max-w-md mx-auto py-16 px-4">
			<div class="bg-white p-8 rounded-lg shadow-lg">
				<h1 class="text-2xl font-semibold mb-6 text-gray-800">Создать курс</h1>
				<form @submit.prevent="createCourse" class="space-y-6">
					<!-- Название -->
					<div>
						<label class="block mb-2 text-sm font-medium text-gray-700"
							>Название курса *</label
						>
						<input
							v-model="title"
							type="text"
							required
							placeholder="Введите название"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>

					<!-- Описание -->
					<div>
						<label class="block mb-2 text-sm font-medium text-gray-700"
							>Описание</label
						>
						<textarea
							v-model="description"
							rows="4"
							placeholder="Краткое описание курса"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						></textarea>
					</div>

					<!-- Часы -->
					<div>
						<label class="block mb-2 text-sm font-medium text-gray-700"
							>Часы *</label
						>
						<input
							v-model.number="hours"
							type="number"
							min="1"
							required
							placeholder="Количество часов"
							class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
						/>
					</div>

					<!-- Изображение -->
					<div>
						<label class="block mb-2 text-sm font-medium text-gray-700"
							>Обложка курса</label
						>
						<input
							type="file"
							accept="image/*"
							@change="onFileSelected"
							class="block w-full text-sm text-gray-600"
						/>
						<p v-if="imageFile" class="mt-2 text-xs text-gray-500">
							Выбран: {{ imageFile.name }}
						</p>
					</div>

					<!-- Кнопка -->
					<div>
						<button
							type="submit"
							class="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
						>
							Создать курс
						</button>
					</div>
				</form>
			</div>
		</main>
	</div>
	<transition name="fade">
		<div
			v-if="showErrorPopup"
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
		>
			<div class="bg-white rounded-lg shadow-lg max-w-sm w-full p-6 relative">
				<button
					@click="closeError"
					class="absolute top-2 right-2 text-gray-500 hover:text-gray-800"
				>
					×
				</button>
				<h3 class="text-lg font-semibold text-red-600 mb-4">Ошибка</h3>
				<p class="text-gray-700">{{ errorMessage }}</p>
				<div class="mt-6 text-right">
					<button
						@click="closeError"
						class="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
					>
						Закрыть
					</button>
				</div>
			</div>
		</div>
	</transition>
</template>

<style scoped>
/* scoped styles, если понадобятся дополнительные правки */
</style>
