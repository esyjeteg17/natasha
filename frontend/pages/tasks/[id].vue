<script setup lang="ts">
type SubmissionState = {
	statusDescription: string
	evaluationStatus: string
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const taskId = route.params.id as string
const taskTitle = ref(
	'Практическое занятие 2. Групповая презентация на тему: Презентация выбранного профиля'
)
const taskDuration = ref('6 акад. час.')
const taskContent = ref<string[]>([])

// Submission state
const submissionState = ref<SubmissionState>({
	statusDescription: 'Ответ на задание должен быть представлен вне сайта',
	evaluationStatus: 'Не оценено',
})

// File upload
const file = ref<File | null>(null)

function onFileSelected(e: Event) {
	const files = (e.target as HTMLInputElement).files
	if (files && files.length > 0) {
		file.value = files[0]
	}
}

async function submitAnswer() {
	if (!authStore.user || authStore.user.role !== 'student') {
		alert('Только студент может отправлять ответы.')
		return
	}
	if (!file.value) {
		alert('Пожалуйста, выберите файл ответа.')
		return
	}

	try {
		const formData = new FormData()
		formData.append('file', file.value)
		formData.append('task', taskId)

		await $fetch('/api/submissions/', {
			baseURL: authStore.baseURL,
			method: 'POST',
			body: formData,
			headers: { Authorization: `Bearer ${authStore.accessToken}` },
		})

		submissionState.value = {
			statusDescription: 'В очереди на проверку',
			evaluationStatus: 'Не оценено',
		}
		alert('Ответ отправлен')
	} catch (err: any) {
		console.error('Ошибка отправки ответа', err)
		alert('Ошибка: ' + (err.data?.detail || err.message))
	}
}

// Load task content (stubbed for now)
onMounted(() => {
	// TODO: Заменить на реальный запрос к API tasks/:id/
	taskContent.value = [
		'Цель работы: научиться работать в команде и заинтересовывать аудиторию.',
		'Данная практическая работа выполняется в группе. Группа может состоять из 2-5 человек...',
		'Также следует определить, кто будет переключать слайды...',
	]
})
</script>

<template>
	<div class="min-h-screen bg-gray-50">
		<div class="max-w-7xl mx-auto py-8">
			<div class="bg-white rounded-lg shadow p-6">
				<!-- Title and Duration -->
				<div class="flex items-baseline justify-between">
					<h1 class="text-2xl font-semibold text-gray-800">{{ taskTitle }}</h1>
					<span class="text-sm text-gray-500">({{ taskDuration }})</span>
				</div>

				<!-- Mark as Completed Button -->
				<button
					class="mt-4 px-4 py-2 border border-blue-600 text-blue-600 rounded hover:bg-blue-50 transition"
				>
					Отметить как выполненный
				</button>

				<hr class="my-6 border-gray-200" />

				<!-- Task Content -->
				<div class="prose prose-gray">
					<p v-for="(paragraph, idx) in taskContent" :key="idx">
						{{ paragraph }}
					</p>
				</div>

				<!-- Submission State -->
				<div class="mt-8">
					<h2 class="text-xl font-semibold mb-4 text-gray-800">
						Состояние ответа
					</h2>
					<table class="w-full text-left border border-gray-200 mb-6">
						<tbody>
							<tr class="bg-gray-50">
								<td class="px-4 py-2 font-medium">
									Состояние ответа на задание
								</td>
								<td class="px-4 py-2">
									{{ submissionState.statusDescription }}
								</td>
							</tr>
							<tr>
								<td class="px-4 py-2 font-medium">Состояние оценивания</td>
								<td class="px-4 py-2">
									{{ submissionState.evaluationStatus }}
								</td>
							</tr>
						</tbody>
					</table>

					<!-- File Upload -->
					<div class="space-y-4">
						<div>
							<label class="block mb-2 text-sm font-medium text-gray-700"
								>Прикрепить ответ</label
							>
							<input
								type="file"
								@change="onFileSelected"
								class="block w-full text-gray-600"
							/>
							<p v-if="file" class="mt-2 text-xs text-gray-500">
								Выбран: {{ file.name }}
							</p>
						</div>
						<button
							@click="submitAnswer"
							:disabled="!file"
							class="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition disabled:opacity-50"
						>
							Отправить ответ
						</button>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>
