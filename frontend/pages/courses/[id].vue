<script setup lang="ts">
type Topic = { id: number; title: string; description: string; order: number }
type Task = { id: number; title: string; topic: number }

const coursesStore = useCoursesStore()
const isAuthenticated = useAuthStore().isAuthenticated

const route = useRoute()
const { id } = route.params

onMounted(() => {
	if (!isAuthenticated) {
		navigateTo('/login')
	}
})

function addTopic() {
	navigateTo({ name: 'topics-create', query: { course: id } })
}

// навигация на создание задания (передаём id темы)
function addTask(topicId: number) {
	navigateTo({ name: 'tasks-create', query: { topic: topicId } })
}

const authStore = useAuthStore()

const isTeacher = computed(() => authStore.user?.role === 'teacher')

await Promise.all([
	coursesStore.getCourse(+id),
	coursesStore.getTopics(+id),
	coursesStore.getTasks(),
])

const tabs = ['Курс', 'Преподаватель и расписание']
const activeTab = ref('Курс')

const sections = computed(() => {
	return coursesStore.currentTopics
		.filter(item => item.course === +id)
		.map(item => {
			return {
				title: item.title,
				description: item.description,
				items: coursesStore.currentTasks.filter(i => i.topic === item.id),
			}
		})
		.sort((a, b) => a.order - b.order)
})

const openSections = ref<string[]>(['Общее'])

function toggleSection(title: string) {
	if (openSections.value.includes(title)) {
		openSections.value = openSections.value.filter(t => t !== title)
	} else {
		openSections.value.push(title)
	}
}

function toggleCompleted(sectionTitle: string, itemId: number) {
	const section = sections.value.find(s => s.title === sectionTitle)
	if (!section) return
	const item = section.items.find(i => i.id === itemId)
	if (item) item.completed = !item.completed
}

const showAddTopicForm = ref(false)
const newTopic = reactive({
	title: '',
	description: '',
	order: sections.value.length + 1,
})
async function createTopic() {
	try {
		// Ensure numeric course ID
		const payload = {
			course: id,
			title: newTopic.title,
			description: newTopic.description,
			order: newTopic.order,
		}
		const response = await fetch(`${authStore.baseURL}/api/topics/`, {
			method: 'POST',
			headers: {
				Authorization: `Bearer ${authStore.accessToken}`,
				'Content-Type': 'application/json',
			},
			body: JSON.stringify(payload),
		})
		if (!response.ok) {
			const err = await response.json()
			console.error('Topic creation error', err)
			alert('Ошибка создания темы: ' + JSON.stringify(err))
			return
		}
		await coursesStore.getTopics(+id)
		newTopic.title = ''
		newTopic.description = ''
		newTopic.order = sections.value.length + 1
		showAddTopicForm.value = false
	} catch (e) {
		console.error(e)
		alert('Ошибка создания темы')
	}
}

// Inline Add Task
const showAddTaskFormFor = ref<number | null>(null)
const newTask = reactive({
	title: '',
	description: '',
	min_words: 100,
	expected_defense_time: 10,
	file: null as File | null,
})
function onTaskFileSelected(e: Event) {
	const files = (e.target as HTMLInputElement).files
	if (files && files.length) newTask.file = files[0]
}
async function createTask(topicId: number) {
	try {
		const formData = new FormData()
		formData.append('topic', topicId)
		formData.append('title', newTask.title)
		formData.append('description', newTask.description)
		formData.append('min_words', String(newTask.min_words))
		formData.append(
			'expected_defense_time',
			String(newTask.expected_defense_time)
		)
		if (newTask.file) formData.append('file', newTask.file)

		// Use native fetch to ensure multipart/form-data
		const response = await fetch(`${authStore.baseURL}/api/tasks/`, {
			method: 'POST',
			headers: { Authorization: `Bearer ${authStore.accessToken}` },
			body: formData,
		})
		if (!response.ok) {
			const err = await response.json()
			console.error('Task creation error', err)
			alert('Ошибка создания задания: ' + JSON.stringify(err))
			return
		}
		await coursesStore.getTasks()
		// reset
		newTask.title = ''
		newTask.description = ''
		newTask.min_words = 100
		newTask.expected_defense_time = 10
		newTask.file = null
		showAddTaskFormFor.value = null
	} catch (e) {
		console.error(e)
		alert('Ошибка создания задания')
	}
}

const currentCourse = computed(() => coursesStore.currentCourse)
const isCurrentTeacher = computed(
	() =>
		authStore.user?.role === 'teacher' &&
		authStore.user?.id === currentCourse.value?.teacher.id
)
const isStudent = computed(() => authStore.user?.role === 'student')

// Список окон расписания
const schedules = ref<Schedule[]>([])

// Форма для создания нового окна (только для преподавателя)
const newWindow = reactive({
	title: '',
	date: '', // yyyy-MM-dd
	start_time: '', // HH:mm:ss
	end_time: '', // HH:mm:ss
})

async function loadSchedules() {
	try {
		const all: Schedule[] = await $fetch('/api/teacher-schedules/', {
			baseURL: authStore.baseURL,
			headers: { Authorization: `Bearer ${authStore.accessToken}` },
		})
		// Если студент — оставляем только окна нужного преподавателя
		if (isStudent.value) {
			schedules.value = all.filter(s => true)
		} else {
			schedules.value = all
		}
	} catch (e) {
		console.error('Не удалось загрузить расписание', e)
	}
}

// создание окна (teacher only)
async function createWindow() {
	try {
		await $fetch('/api/teacher-schedules/', {
			baseURL: authStore.baseURL,
			method: 'POST',
			headers: {
				Authorization: `Bearer ${authStore.accessToken}`,
				'Content-Type': 'application/json',
			},
			body: { ...newWindow },
		})
		// сброс формы
		newWindow.title =
			newWindow.date =
			newWindow.start_time =
			newWindow.end_time =
				''
		await loadSchedules()
	} catch (err: any) {
		alert('Ошибка создания окна: ' + JSON.stringify(err.data || err))
	}
}

// студент записывается
async function signup(slotId: number) {
	try {
		await fetch(
			`${authStore.baseURL}/api/teacher-schedules/${slotId}/signup/`,
			{
				method: 'POST',
				headers: { Authorization: `Bearer ${authStore.accessToken}` },
			}
		)
		await loadSchedules()
	} catch (err: any) {
		alert('Не получилось записаться: ' + JSON.stringify(err.data || err))
	}
}
// студент отменяет запись
async function cancelSignup(slotId: number) {
	try {
		await fetch(
			`${authStore.baseURL}/api/teacher-schedules/${slotId}/cancel_signup/`,
			{
				method: 'DELETE',
				headers: { Authorization: `Bearer ${authStore.accessToken}` },
			}
		)
		await loadSchedules()
	} catch (err: any) {
		alert('Не получилось отменить запись: ' + JSON.stringify(err.data || err))
	}
}

onMounted(async () => {
	if (!authStore.isAuthenticated) {
		navigateTo('/login')
	}
	// сначала нужно загрузить курс
	await coursesStore.getCourse(+route.params.id)
	await loadSchedules()
})
</script>
<template>
	<div class="w-full max-w-7xl mx-auto py-6">
		<div class="flex items-center justify-between mb-6">
			<h1 class="text-2xl font-semibold">
				{{ coursesStore.currentCourse?.title }}
			</h1>
			<div class="flex space-x-4">
				<NuxtLink
					:to="{
						name: 'my-courses',
					}"
					class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
				>
					Дисциплины
				</NuxtLink>
			</div>
		</div>

		<img
			v-if="coursesStore.currentCourse?.img"
			:src="coursesStore.currentCourse?.img"
			alt=""
			class="w-full h-72 my-6 rounded-lg object-cover"
		/>

		<nav class="border-b border-gray-200 mb-4">
			<ul class="flex -mb-px">
				<li
					v-for="tab in tabs"
					:key="tab"
					@click="activeTab = tab"
					class="mr-4 cursor-pointer pb-2"
					:class="
						activeTab === tab
							? 'border-b-2 border-blue-600 text-blue-600'
							: 'text-gray-600 hover:text-gray-800'
					"
				>
					{{ tab }}
				</li>
			</ul>
		</nav>

		<div v-if="activeTab === 'Курс'">
			<div class="flex justify-end mb-4" v-if="isTeacher">
				<button
					@click="showAddTopicForm = true"
					class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
				>
					+ Добавить тему
				</button>
			</div>
			<div v-if="showAddTopicForm" class="bg-white p-6 rounded-lg shadow mb-6">
				<h3 class="text-lg font-medium mb-4">Новая тема</h3>
				<div class="space-y-4">
					<input
						v-model="newTopic.title"
						type="text"
						placeholder="Название темы"
						class="w-full px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
					/>
					<textarea
						v-model="newTopic.description"
						rows="3"
						placeholder="Описание темы"
						class="w-full px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
					></textarea>
					<input
						v-model.number="newTopic.order"
						type="number"
						min="1"
						placeholder="Порядок"
						class="w-24 px-4 py-2 border rounded focus:ring-2 focus:ring-blue-500"
					/>
					<div class="flex space-x-2">
						<button
							@click="createTopic"
							class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
						>
							Сохранить
						</button>
						<button
							@click="showAddTopicForm = false"
							class="px-4 py-2 border rounded hover:bg-gray-100"
						>
							Отмена
						</button>
					</div>
				</div>
			</div>

			<div v-for="section in sections" :key="section.title" class="mb-6">
				<button
					class="w-full flex justify-between items-center bg-gray-100 p-4 rounded-t-md focus:outline-none"
					@click="toggleSection(section.title)"
				>
					<span class="font-medium text-lg">{{ section.title }}</span>
					<IconsArrowTop
						class="w-6 h-6"
						:class="{
							'transform rotate-180': !openSections.includes(section.title),
						}"
					/>
				</button>

				<div
					v-show="openSections.includes(section.title)"
					class="border border-t-0 border-gray-200 p-4 rounded-b-md"
				>
					<p v-if="section.description" class="text-gray-700 mb-4">
						{{ section.description }}
					</p>
					<ul>
						<li
							v-for="item in section.items"
							:key="item.id"
							class="flex items-center justify-between p-4 border-b last:border-b-0"
						>
							<div class="flex items-center gap-2">
								<IconsTask />
								<NuxtLink
									:to="`/tasks/${item.id}`"
									class="font-medium text-gray-800"
								>
									{{ item.title }}
								</NuxtLink>
							</div>

							<button
								v-if="!isTeacher"
								class="px-3 py-1 border rounded"
								:class="
									item.completed
										? 'bg-green-600 text-white border-green-600'
										: 'text-blue-600 border-blue-600 hover:bg-blue-50'
								"
								@click="toggleCompleted(section.title, item.id)"
							>
								{{ item.completed ? 'Выполнено' : 'Отметить как выполненный' }}
							</button>
						</li>
					</ul>
					<div v-if="isTeacher">
						<button
							v-if="showAddTaskFormFor !== section.items[0]?.id"
							@click="showAddTaskFormFor = section.items[0]?.id"
							class="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
						>
							+ Добавить задание
						</button>
						<div
							v-else-if="showAddTaskFormFor === section.items[0]?.id"
							class="bg-gray-50 p-4 rounded space-y-3"
						>
							<h3 class="text-lg font-medium">Новое задание</h3>
							<input
								v-model="newTask.title"
								type="text"
								placeholder="Название задания"
								class="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
							/>
							<textarea
								v-model="newTask.description"
								rows="2"
								placeholder="Описание"
								class="w-full px-3 py-2 border rounded focus:ring-2 focus:ring-blue-500"
							></textarea>
							<div class="flex space-x-2">
								<input
									v-model.number="newTask.min_words"
									type="number"
									min="1"
									placeholder="Мин. слов"
									class="w-24 px-2 py-2 border rounded focus:ring-2 focus:ring-blue-500"
								/>
								<input
									v-model.number="newTask.expected_defense_time"
									type="number"
									min="1"
									placeholder="Мин защиты"
									class="w-24 px-2 py-2 border rounded focus:ring-2 focus:ring-blue-500"
								/>
							</div>
							<div>
								<input
									type="file"
									@change="onTaskFileSelected"
									class="block text-gray-600"
								/>
								<p v-if="newTask.file" class="text-xs text-gray-500">
									{{ newTask.file.name }}
								</p>
							</div>
							<div class="flex space-x-2">
								<button
									@click="
										createTask(
											section.items[0]?.topic
												? Number(section.items[0]?.topic)
												: coursesStore.currentTopics.find(
														t => t.title === section?.title
												  )?.id
										)
									"
									class="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
								>
									Сохранить
								</button>
								<button
									@click="showAddTaskFormFor = null"
									class="px-4 py-2 border rounded hover:bg-gray-100"
								>
									Отмена
								</button>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<div v-else-if="activeTab === 'Преподаватель и расписание'">
			<div
				class="flex flex-col md:flex-row items-center md:items-start gap-10 py-6"
			>
				<!-- Фото -->
				<img
					src="/img/profile.png"
					alt="Фото преподавателя"
					class="w-32 h-32 rounded-full object-cover"
				/>

				<!-- Основные данные -->
				<div class="flex-1 space-y-2">
					<h2 class="text-2xl font-semibold text-gray-800">
						{{ coursesStore.currentCourse.teacher.first_name }}
						{{ coursesStore.currentCourse.teacher.last_name }}
					</h2>
					<p class="text-gray-600">
						<span class="font-medium">Email: </span>
						<a
							:href="`mailto:${coursesStore.currentCourse.teacher.email}`"
							class="text-blue-600 hover:underline"
						>
							{{ coursesStore.currentCourse.teacher.email }}
						</a>
					</p>
					<p class="text-gray-600">
						<span class="font-medium">Телефон:</span>
						{{ coursesStore.currentCourse.teacher.phone || 'Не указан' }}
					</p>
					<p class="text-gray-600">
						<span class="font-medium">Дата регистрации:</span>
						{{
							new Date(
								coursesStore.currentCourse.teacher.date_joined
							).toLocaleDateString()
						}}
					</p>
				</div>
			</div>
			<section class="mt-8">
				<h2
					v-if="isCurrentTeacher || isStudent"
					class="text-2xl flex items-center gap-3 font-semibold mb-4"
				>
					Расписание приёмных окон
					<button @click="loadSchedules">
						<IconsReload class="w-5 h-5" />
					</button>
				</h2>

				<!-- форма добавления (только для самого преподавателя) -->
				<div v-if="isCurrentTeacher" class="mb-6 bg-white p-4 rounded shadow">
					<h3 class="font-medium mb-2">Добавить новое окно</h3>
					<div class="grid grid-cols-1 md:grid-cols-4 gap-3">
						<input
							v-model="newWindow.title"
							placeholder="Заголовок"
							class="border p-2 rounded"
						/>
						<input
							v-model="newWindow.date"
							type="date"
							class="border p-2 rounded"
						/>
						<input
							v-model="newWindow.start_time"
							type="time"
							class="border p-2 rounded"
						/>
						<input
							v-model="newWindow.end_time"
							type="time"
							class="border p-2 rounded"
						/>
					</div>
					<button
						@click="createWindow"
						class="mt-3 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
					>
						Сохранить
					</button>
				</div>

				<!-- список окон -->
				<div class="space-y-4">
					<div
						v-for="slot in schedules.filter(
							s => s.teacher.id === coursesStore.currentCourse.teacher.id
						)"
						:key="slot.id"
						class="bg-white p-4 rounded shadow flex flex-col md:flex-row md:justify-between md:items-center"
					>
						<div>
							<p class="font-medium">{{ slot.title }}</p>
							<p class="text-sm text-gray-600">
								{{ new Date(slot.date).toLocaleDateString() }}
								({{
									new Date(slot.date).toLocaleString('ru-RU', {
										weekday: 'long',
									})
								}}) с {{ slot.start_time.slice(0, 5) }} до
								{{ slot.end_time.slice(0, 5) }} ({{ slot.duration_minutes }}
								мин)
							</p>
							<p class="text-sm">
								Свободно: {{ slot.available_slots }} / {{ slot.max_slots }}
							</p>
						</div>

						<!-- действия -->
						<div class="mt-3 md:mt-0 space-x-2">
							<!-- студент -->
							<button
								v-if="isStudent"
								@click="
									slot.appointments.some(
										a =>
											a.first_name === authStore.user?.first_name &&
											a.last_name === authStore.user?.last_name
									)
										? cancelSignup(slot.id)
										: signup(slot.id)
								"
								:class="[
									'px-3 py-1 rounded font-medium',
									slot.appointments.some(
										a =>
											a.first_name === authStore.user?.first_name &&
											a.last_name === authStore.user?.last_name
									)
										? 'bg-red-600 text-white hover:bg-red-700'
										: 'bg-blue-600 text-white hover:bg-blue-700',
								]"
							>
								{{
									slot.appointments.some(
										a =>
											a.first_name === authStore.user?.first_name &&
											a.last_name === authStore.user?.last_name
									)
										? 'Отменить запись'
										: 'Записаться'
								}}
							</button>

							<!-- преподаватель видит список записавшихся -->
							<ul v-if="isCurrentTeacher" class="mt-4 space-y-1 text-sm">
								<li
									v-for="appt in slot.appointments"
									:key="appt.id"
									class="flex justify-between px-2"
								>
									<span
										>{{ appt.position }}. {{ appt.first_name }}
										{{ appt.last_name }}</span
									>
								</li>
								<li v-if="!slot.appointments.length" class="text-gray-500">
									Никто не записан
								</li>
							</ul>
						</div>
					</div>
				</div>
			</section>
		</div>

		<!-- Placeholder for other tabs -->
		<div v-else class="p-4 text-gray-500">
			Содержание раздела «{{ activeTab }}» пока не реализовано.
		</div>
	</div>
</template>
