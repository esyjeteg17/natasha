<script setup lang="ts">
const authStore = useAuthStore()
const router = useRouter()

const title = ref('')
const description = ref('')
const hours = ref(36)
const infoFile = ref<File | null>(null)

onMounted(() => {
	if (!authStore.isTeacher) {
		alert('У вас нет прав для создания курса')
		router.push('/')
	}
})

function onFileSelected(e: Event) {
	const files = (e.target as HTMLInputElement).files
	if (files && files.length > 0) {
		infoFile.value = files[0]
	}
}

async function createCourse() {
	if (!authStore.isTeacher) {
		alert('Только преподаватель может создавать курс')
		return
	}

	try {
		const formData = new FormData()
		formData.append('title', title.value)
		formData.append('description', description.value)
		formData.append('hours', String(hours.value))
		if (infoFile.value) {
			formData.append('info_file', infoFile.value)
		}

		const response = await $fetch('/api/courses/', {
			baseURL: authStore.baseURL,
			method: 'POST',
			body: formData,
			headers: {
				Authorization: `Bearer ${authStore.accessToken}`,
			},
		})
		alert('Курс успешно создан')
		router.push('/courses')
	} catch (error: any) {
		console.error('Ошибка создания курса', error)
		alert('Ошибка создания курса: ' + error.data?.detail || error.message)
	}
}
</script>

<template>
	<div class="max-w-lg mx-auto mt-10 bg-white p-4 shadow">
		<h1 class="text-2xl mb-4 font-bold">Создать курс</h1>
		<form @submit.prevent="createCourse">
			<div class="mb-4">
				<label class="block font-medium mb-1">Название курса</label>
				<input v-model="title" type="text" class="border w-full p-2" />
			</div>

			<div class="mb-4">
				<label class="block font-medium mb-1">Описание</label>
				<textarea v-model="description" class="border w-full p-2"></textarea>
			</div>

			<div class="mb-4">
				<label class="block font-medium mb-1">Часы</label>
				<input
					v-model="hours"
					type="number"
					min="1"
					class="border w-full p-2"
				/>
			</div>

			<div class="mb-4">
				<label class="block font-medium mb-1"
					>Доп. файл (PDF, DOC и т.п.)</label
				>
				<input type="file" @change="onFileSelected" />
			</div>
			<button type="submit" class="bg-blue-500 text-white py-2 px-4">
				Создать
			</button>
		</form>
	</div>
</template>
