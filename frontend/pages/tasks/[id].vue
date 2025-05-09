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

// структура ответа AI
type AIResult = {
	evaluation: string
	keywords: { keyword: string; count: number }[]
	extracted_topic: string
	word_count: number
	passed: boolean
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const coursesStore = useCoursesStore()

const idAIChecking = ref(false)

onMounted(() => {
	if (!authStore.isAuthenticated) router.push('/login')
})

const taskId = Number(route.params.id)
const currentTask = computed(() =>
	coursesStore.currentTasks.find(t => t.id === taskId)
)
const currentTopic = computed(() =>
	coursesStore.currentTopics.find(t => t.id === currentTask.value?.topic)
)

const submissions = ref<Submission[]>([])
const isTeacher = computed(() => authStore.user?.role === 'teacher')

async function loadSubmissions() {
	try {
		const { results, ...rest }: any = await $fetch('/api/submissions/', {
			baseURL: authStore.baseURL,
			headers: { Authorization: `Bearer ${authStore.accessToken}` },
			params: { task: taskId },
		})
		const subs = results || rest
		submissions.value = subs
			.filter((s: Submission) => s.status === 'waiting_for_check')
			.sort(
				(a, b) =>
					new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
			)
	} catch (e) {
		console.error('Не удалось загрузить ответы', e)
	}
}
onMounted(loadSubmissions)

const file = ref<File | null>(null)
function onFileSelected(e: Event) {
	const files = (e.target as HTMLInputElement).files
	if (files && files.length) file.value = files[0]
}

// результат от AI и управление модалкой
const aiResult = ref<AIResult | null>(null)
const showAIModal = ref(false)

// запускаем AI-проверку
async function runDocReview(file: File, topic: string) {
	idAIChecking.value = true
	const form = new FormData()
	form.append('file', file)
	form.append('topic', topic)
	const resp = await fetch(`${authStore.baseURL}/api/doc-review/`, {
		method: 'POST',
		headers: { Authorization: `Bearer ${authStore.accessToken}` },
		body: form,
	})
	if (!resp.ok) {
		const err = await resp.json().catch(() => null)
		console.error('AI review error', err)
		aiResult.value = {
			evaluation: 'Ошибка AI-сервиса.',
			keywords: [],
			extracted_topic: '',
			word_count: 0,
			passed: false,
		}
	} else {
		aiResult.value = await resp.json()
	}
	showAIModal.value = true
	idAIChecking.value = false
}

// вызывается при нажатии «Отправить ответ»
async function confirmSubmission() {
	if (!file.value) return
	try {
		const formData = new FormData()
		formData.append('file', file.value)
		formData.append('task', String(taskId))
		const created: any = await $fetch('/api/submissions/', {
			baseURL: authStore.baseURL,
			method: 'POST',
			headers: { Authorization: `Bearer ${authStore.accessToken}` },
			body: formData,
		})
		submissions.value.unshift(created)
		showAIModal.value = false
		file.value = null
	} catch (e: any) {
		console.error('Ошибка отправки ответа', e)
	}
}

// основная кнопка: сначала AI, потом откроется модалка
async function submitAnswer() {
	if (authStore.user?.role !== 'student') return
	if (!file.value) return
	if (!currentTopic.value) return
	await runDocReview(file.value, currentTopic.value.title)
}

// статус / AI-прохождение
const getSubmStatus = (status: string) => {
	if (status === 'waiting_for_check') return 'Ожидает проверки'
	if (status === 'approved') return 'Принято'
	if (status === 'rejected') return 'Отклонено'
	return status
}
const getAICheckedText = (passed: boolean) =>
	passed ? 'Пройдена' : 'Не пройдена'

// статус преподавателя
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
		if (resp.ok) sub.status = newStatus
	} catch (e) {
		console.error(e)
	}
}
</script>

<template>
	<div class="min-h-screen bg-gray-50">
		<div class="max-w-7xl mx-auto py-8 px-4">
			<div v-if="currentTask" class="bg-white rounded-lg shadow p-6 space-y-6">
				<!-- Заголовок и файл -->
				<div class="flex justify-between items-baseline">
					<h1 class="text-2xl font-semibold">{{ currentTask.title }}</h1>
					<span class="text-sm text-gray-500">
						({{ currentTask.expected_defense_time }} мин)
					</span>
				</div>
				<div v-if="currentTask.file">
					<a
						:href="currentTask.file"
						target="_blank"
						class="inline-flex items-center text-blue-600 hover:underline"
					>
						<IconsDownloadFile class="w-5 h-5 mr-2" /> Скачать файл задания
					</a>
				</div>

				<!-- Вид студента -->
				<div v-if="!isTeacher">
					<p class="mb-4">{{ currentTask.description }}</p>
					<div class="space-y-4 mb-6">
						<input
							type="file"
							accept=".docx"
							@change="onFileSelected"
							class="block w-full"
						/>
						<button
							class="px-6 py-2 flex items-center bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
							:disabled="!file || idAIChecking"
							@click="submitAnswer"
						>
							<IconsSpiner v-if="idAIChecking" class="w-5 h-5 mr-2" />
							Отправить ответ
						</button>
					</div>

					<!-- Список своих ответов -->
					<h2 class="text-xl font-semibold mb-4">Мои ответы</h2>
					<table class="w-full table-auto border border-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th class="px-4 py-2">Файл</th>
								<th class="px-4 py-2">Дата</th>
								<th class="px-4 py-2">ИИ</th>
								<th class="px-4 py-2">Статус</th>
							</tr>
						</thead>
						<tbody>
							<tr v-for="sub in submissions" :key="sub.id" class="border-t">
								<td class="px-4 py-2">
									<a :href="sub.file" target="_blank" class="text-blue-600">
										Скачать
									</a>
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
								<td colspan="4" class="py-4 text-center text-gray-500">
									Нет ответов
								</td>
							</tr>
						</tbody>
					</table>
				</div>

				<!-- Вид преподавателя -->
				<div v-else>
					<h2 class="text-xl font-semibold mb-4">Ответы студентов</h2>
					<table class="w-full table-auto border border-gray-200">
						<thead class="bg-gray-50">
							<tr>
								<th class="px-4 py-2">Студент</th>
								<th class="px-4 py-2">Файл</th>
								<th class="px-4 py-2">Дата</th>
								<th class="px-4 py-2">ИИ</th>
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
									<a :href="sub.file" target="_blank" class="text-blue-600">
										Скачать
									</a>
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
										class="px-2 py-1 bg-green-600 text-white rounded"
									>
										Принять
									</button>
									<button
										v-if="sub.status !== 'rejected'"
										@click="changeSubmissionStatus(sub, 'rejected')"
										class="px-2 py-1 bg-red-600 text-white rounded"
									>
										Отклонить
									</button>
								</td>
							</tr>
							<tr v-if="!submissions.length">
								<td colspan="6" class="py-4 text-center text-gray-500">
									Нет ответов
								</td>
							</tr>
						</tbody>
					</table>
				</div>
			</div>

			<div v-else class="text-center text-gray-500">Задание не найдено.</div>
		</div>

		<!-- Модалка с результатами AI -->
		<div
			v-if="showAIModal && aiResult"
			class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4"
		>
			<div class="bg-white rounded-lg shadow-xl max-w-xl w-full p-6 space-y-4">
				<h3 class="text-lg font-semibold">
					Результаты AI-проверки
					<span
						:class="aiResult.passed ? 'text-green-600' : 'text-red-600'"
						class="ml-2"
					>
						{{ aiResult.passed ? 'Пройдено' : 'Не пройдено' }}
					</span>
				</h3>
				<p><b>Тема, извлечённая AI:</b> {{ aiResult.extracted_topic }}</p>
				<p><b>Всего слов:</b> {{ aiResult.word_count }}</p>
				<div>
					<b>Ключевые слова:</b>
					<ul class="list-disc list-inside">
						<li v-for="kw in aiResult.keywords" :key="kw.keyword">
							{{ kw.keyword }} ({{ kw.count }})
						</li>
					</ul>
				</div>
				<div>
					<b>Оценка AI:</b>
					<div class="mt-2 p-4 bg-gray-50 rounded max-h-60 overflow-auto">
						<pre class="whitespace-pre-wrap">{{ aiResult.evaluation }}</pre>
					</div>
				</div>
				<div class="flex justify-end space-x-2">
					<button
						class="px-4 py-2 border rounded hover:bg-gray-100"
						@click="showAIModal = false"
					>
						Закрыть
					</button>
					<button
						v-if="aiResult.passed"
						class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
						@click="confirmSubmission"
					>
						Подтвердить и отправить
					</button>
				</div>
			</div>
		</div>
	</div>
</template>
