<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCoursesStore } from '@/stores/courses'

type Submission = {
	id: number
	file: string
	created_at: string
	student: { first_name: string; last_name: string }
	status: string
	ai_check_passed: boolean
}

type SubmissionState = {
	statusDescription: string
	evaluationStatus: string
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const coursesStore = useCoursesStore()

// Redirect if not authenticated
onMounted(() => {
	if (!authStore.isAuthenticated) router.push('/login')
})

// Current task and its topic
const taskId = Number(route.params.id)
const currentTask = computed(() =>
	coursesStore.currentTasks.find(task => task.id === taskId)
)
const currentTopic = computed(() =>
	coursesStore.currentTopics.find(
		topic => topic.id === currentTask.value?.topic
	)
)

// Submission list
const submissions = ref<Submission[]>([])
const isTeacher = computed(() => authStore.user?.role === 'teacher')

// Load submissions filtered by task
onMounted(async () => {
	try {
		const { results, ...rest }: any = await $fetch('/api/submissions/', {
			baseURL: authStore.baseURL,
			headers: { Authorization: `Bearer ${authStore.accessToken}` },
			params: { task: taskId },
		})
		const subs = results || rest
		submissions.value = subs
			?.filter((s: Submission) => s.status === 'waiting_for_check')
			?.sort(
				(a, b) =>
					new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
			)
	} catch (e) {
		console.error('Не удалось загрузить ответы', e)
	}
})

// Helpers
const getSubmStatus = (status: string) => {
	if (status === 'waiting_for_check') return 'Ожидает проверки'
	if (status === 'approved') return 'Принято'
	if (status === 'rejected') return 'Отклонено'
	return status
}
const getAICheckedText = (passed: boolean) =>
	passed ? 'Пройдена' : 'Не пройдена'

// File upload for students
const file = ref<File | null>(null)
function onFileSelected(e: Event) {
	const files = (e.target as HTMLInputElement).files
	if (files && files.length) file.value = files[0]
}

// Run AI review via doc-review endpoint
async function runDocReview(file: File, topic: string): Promise<boolean> {
	const form = new FormData()
	form.append('file', file)
	form.append('topic', topic)
	const resp = await fetch(`${authStore.baseURL}/api/doc-review/`, {
		method: 'POST',
		headers: { Authorization: `Bearer ${authStore.accessToken}` },
		body: form,
	})
	if (!resp.ok) {
		const err = await resp.json()
		console.error('AI review error', err)
		alert('AI тест не прошёл: ' + JSON.stringify(err))
		return false
	}
	const result: any = await resp.json()
	return result.passed === true
}

// Submit answer: first run AI review, then create submission
async function submitAnswer() {
	if (authStore.user?.role !== 'student') {
		alert('Только студент может отправлять ответы.')
		return
	}
	if (!file.value) {
		alert('Пожалуйста, выберите файл ответа.')
		return
	}
	if (!currentTopic.value) {
		alert('Не найдена тема задания.')
		return
	}
	// AI check
	const passed = await runDocReview(file.value, currentTopic.value.title)
	if (!passed) return
	// Proceed to submission
	try {
		const formData = new FormData()
		formData.append('file', file.value)
		formData.append('task', String(taskId))
		const resp: any = await $fetch('/api/submissions/', {
			baseURL: authStore.baseURL,
			method: 'POST',
			body: formData,
			headers: { Authorization: `Bearer ${authStore.accessToken}` },
		})
		submissions.value.push(resp)
		alert('Ответ отправлен и ожидает проверки')
	} catch (err: any) {
		console.error('Ошибка отправки ответа', err)
		alert('Ошибка: ' + (err.data?.detail || err.message))
	}
}

// Change status by teacher
async function changeSubmissionStatus(sub: Submission, newStatus: string) {
	try {
		const resp = await fetch(
			`${authStore.baseURL}/api/submissions/${sub.id}/`,
			{
				method: 'PATCH',
				headers: {
					Authorization: `Bearer ${authStore.accessToken}`,
					'Content-Type': 'application/json',
				},
				body: JSON.stringify({ status: newStatus }),
			}
		)
		if (!resp.ok) {
			const err = await resp.json()
			console.error('Error updating submission', err)
			alert('Не удалось изменить статус: ' + JSON.stringify(err))
			return
		}
		sub.status = newStatus
	} catch (e) {
		console.error(e)
		alert('Ошибка при отправке запроса')
	}
}
</script>

<template>
	<div class="min-h-screen bg-gray-50">
		<div class="max-w-7xl mx-auto py-8 px-4">
			<div v-if="currentTask" class="bg-white rounded-lg shadow p-6 space-y-6">
				<!-- Header -->
				<div class="flex items-baseline justify-between">
					<h1 class="text-2xl font-semibold text-gray-800">
						{{ currentTask.title }}
					</h1>
					<span class="text-sm text-gray-500"
						>({{ currentTask.expected_defense_time }} мин)</span
					>
				</div>
				<!-- Download Task File -->
				<div v-if="currentTask.file">
					<a
						:href="currentTask.file"
						target="_blank"
						class="inline-flex items-center text-blue-600 hover:underline"
					>
						<IconsDownloadFile class="w-5 h-5 mr-2 text-gray-600" /> Скачать
						файл задания
					</a>
				</div>
				<!-- Student View -->
				<div v-if="!isTeacher">
					<div class="prose prose-gray mb-4">
						<p>{{ currentTask.description }}</p>
					</div>
					<p class="text-gray-700 mb-4">
						<span class="font-medium">Мин. слов:</span>
						{{ currentTask.min_words }}
					</p>
					<!-- Submission form -->
					<div class="space-y-4 mb-6">
						<div>
							<label class="block mb-2 text-sm font-medium text-gray-700"
								>Прикрепить ответ</label
							>
							<input
								type="file"
								@change="onFileSelected"
								class="block w-full text-gray-600"
								accept=".doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
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
					<!-- Student Submissions List -->
					<h2 class="text-xl font-semibold mb-4 text-gray-800">Мои ответы</h2>
					<table class="w-full text-left border border-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th class="px-4 py-2">Файл</th>
								<th class="px-4 py-2">Дата</th>
								<th class="px-4 py-2">ИИ Проверка</th>
								<th class="px-4 py-2">Статус</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="sub in submissions" :key="sub.id" class="border-t">
								<td class="px-4 py-2">
									<a
										:href="sub.file"
										target="_blank"
										class="text-blue-600 hover:underline"
										>Скачать</a
									>
								</td>
								<td class="px-4 py-2">
									{{ new Date(sub.created_at).toLocaleString() }}
								</td>
								<td class="px-4 py-2">
									{{ getAICheckedText(sub.ai_check_passed) }}
								</td>
								<td class="px-4 py-2">{{ getSubmStatus(sub.status) }}</td>
							</tr>
							<tr v-if="!submissions.length">
								<td colspan="4" class="px-4 py-2 text-center text-gray-500">
									Нет ответов
								</td>
							</tr>
						</tbody>
					</table>
				</div>
				<!-- Teacher View -->
				<div v-else>
					<h2 class="text-xl font-semibold mb-4 text-gray-800">
						Ответы студентов
					</h2>
					<table class="w-full text-left border border-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th class="px-4 py-2">Студент</th>
								<th class="px-4 py-2">Файл</th>
								<th class="px-4 py-2">Дата</th>
								<th class="px-4 py-2">ИИ проверка</th>
								<th class="px-4 py-2">Статус</th>
								<th class="px-4 py-2">Действие</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="sub in submissions" :key="sub.id" class="border-t">
								<td class="px-4 py-2">
									{{ sub.student.first_name }} {{ sub.student.last_name }}
								</td>
								<td class="px-4 py-2">
									<a
										:href="sub.file"
										target="_blank"
										class="text-blue-600 hover:underline"
										>Скачать</a
									>
								</td>
								<td class="px-4 py-2">
									{{ new Date(sub.created_at).toLocaleString() }}
								</td>
								<td class="px-4 py-2">
									{{ getAICheckedText(sub.ai_check_passed) }}
								</td>
								<td class="px-4 py-2">{{ getSubmStatus(sub.status) }}</td>
								<td class="px-4 py-2 space-x-2">
									<button
										v-if="sub.status !== 'approved'"
										@click="changeSubmissionStatus(sub, 'approved')"
										class="px-2 py-1 bg-green-600 text-white rounded hover:bg-green-700"
									>
										Принять
									</button>
									<button
										v-if="sub.status !== 'rejected'"
										@click="changeSubmissionStatus(sub, 'rejected')"
										class="px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700"
									>
										Отклонить
									</button>
								</td>
							</tr>
							<tr v-if="!submissions.length">
								<td colspan="6" class="px-4 py-2 text-center text-gray-500">
									Нет ответов
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>
			<div v-else class="text-center text-gray-500">Задание не найдено.</div>
		</div>
	</div>
</template>
