<script setup lang="ts">
// статические данные курса
const course = {
	id: 102,
	slug: 'python',
	img: '/img/courses/scale_1200.jpeg',
	title: 'Продвинутый Python для аналитиков',
	teacher: {
		id: 2,
		first_name: 'Наташа',
		last_name: 'Котюшева',
		email: 'natasha.kotyusheva@mail.com',
		phone: '+7 (912) 345-67-89',
		date_joined: '2024-02-20',
	},
}

// статические темы и задания
const sections = [
	{
		title: 'Введение в Python',
		description: 'Основы синтаксиса, коллекции и управление потоком.',
		items: [
			{ id: 401, title: 'Типы данных и переменные', completed: false },
			{ id: 402, title: 'Списки, кортежи и словари', completed: false },
		],
	},
	{
		title: 'Pandas и обработка данных',
		description: 'Чтение CSV, фильтрация, агрегация и группировка.',
		items: [
			{ id: 411, title: 'Серия и DataFrame', completed: false },
			{ id: 412, title: 'Группировка и сводные таблицы', completed: false },
		],
	},
	{
		title: 'Визуализация данных',
		description: 'Построение графиков с matplotlib и seaborn.',
		items: [
			{ id: 421, title: 'Линейные и столбчатые графики', completed: false },
			{ id: 422, title: 'Корреляционные тепловые карты', completed: false },
		],
	},
]

// статические слоты расписания
const uniqueDates = ['2025-06-01', '2025-06-02', '2025-06-03']
const byDate: Record<string, any[]> = {
	'2025-06-01': [
		{
			id: 501,
			title: 'Утреннее окно',
			start_time: '09:00',
			end_time: '09:15',
			appointments: [{ position: 1, first_name: 'Иван', last_name: 'Петров' }],
			max_slots: 4,
		},
		{
			id: 502,
			title: 'Дневное окно',
			start_time: '12:00',
			end_time: '12:15',
			appointments: [],
			max_slots: 4,
		},
	],
	'2025-06-02': [
		{
			id: 503,
			title: 'Утреннее окно',
			start_time: '09:00',
			end_time: '09:15',
			appointments: [
				{ position: 1, first_name: 'Ольга', last_name: 'Смирнова' },
			],
			max_slots: 4,
		},
	],
	'2025-06-03': [
		{
			id: 504,
			title: 'Вечернее окно',
			start_time: '18:00',
			end_time: '18:15',
			appointments: [],
			max_slots: 4,
		},
	],
}

const sect = ref<'course' | 'schedule'>('course')
const opened = ref<number | null>(null)
function toggle(id: number) {
	opened.value = opened.value === id ? null : id
}
function formatDate(d: string) {
	const dt = new Date(d)
	return dt.toLocaleDateString('ru-RU', { day: '2-digit', month: 'short' })
}
function formatWeekday(d: string) {
	const dt = new Date(d)
	return dt.toLocaleDateString('ru-RU', { weekday: 'short' })
}
</script>

<template>
	<div class="max-w-7xl mx-auto py-6 space-y-6">
		<!-- Карточка курса -->
		<CourseItemMain
			class="mb-6 block"
			:id="course.id"
			:slug="course.slug"
			:img="course.img"
			:title="course.title"
			:teacher="`${course.teacher.first_name} ${course.teacher.last_name}`"
			date="28 фев 2025"
		/>

		<!-- Вкладки -->
		<nav class="border-b border-gray-200">
			<ul class="flex -mb-px">
				<li
					@click="sect = 'course'"
					class="cursor-pointer mr-4 pb-2 border-b-2"
					:class="
						sect === 'course'
							? 'border-blue-600 text-blue-600'
							: 'text-gray-600 hover:text-gray-800'
					"
				>
					Курс
				</li>
				<li
					@click="sect = 'schedule'"
					class="cursor-pointer pb-2 border-b-2"
					:class="
						sect === 'schedule'
							? 'border-blue-600 text-blue-600'
							: 'text-gray-600 hover:text-gray-800'
					"
				>
					Преподаватель и расписание
				</li>
			</ul>
		</nav>

		<!-- Секции с темами -->
		<div v-if="sect === 'course'">
			<div
				v-for="section in sections"
				:key="section.title"
				class="bg-white rounded-lg shadow mb-4"
			>
				<button
					@click="toggle(section.title)"
					class="w-full flex justify-between items-center p-4 text-lg font-medium"
				>
					{{ section.title }}
					<IconsArrowTop
						class="w-5 h-5"
						:class="{ 'rotate-180': opened === section.title }"
					/>
				</button>
				<div v-show="opened === section.title" class="p-4 border-t">
					<p v-if="section.description" class="mb-4 text-gray-700">
						{{ section.description }}
					</p>
					<ul class="space-y-2">
						<li
							v-for="item in section.items"
							:key="item.id"
							class="flex justify-between"
						>
							<div class="flex items-center gap-2">
								<IconsTask class="w-5 h-5 text-blue-600" />
								<span>{{ item.title }}</span>
							</div>
							<button
								class="text-xs px-2 py-1 rounded border"
								:class="
									item.completed
										? 'bg-green-600 text-white'
										: 'text-blue-600 border-blue-600 hover:bg-blue-50'
								"
							>
								{{ item.completed ? 'Выполнено' : 'Отметить' }}
							</button>
						</li>
					</ul>
				</div>
			</div>
		</div>

		<!-- Преподаватель и расписание -->
		<section v-if="sect === 'schedule'" class="bg-white rounded-lg shadow p-6">
			<h2 class="text-2xl font-semibold mb-4">Преподаватель и расписание</h2>
			<div class="flex items-center mb-6 gap-6">
				<img
					src="/img/profile.png"
					class="w-24 h-24 rounded-full object-cover"
				/>
				<div>
					<h3 class="text-xl font-medium">
						{{ course.teacher.first_name }} {{ course.teacher.last_name }}
					</h3>
					<p class="text-gray-600">
						Email:
						<a :href="`mailto:${course.teacher.email}`" class="text-blue-600">{{
							course.teacher.email
						}}</a>
					</p>
					<p class="text-gray-600">Телефон: {{ course.teacher.phone }}</p>
				</div>
			</div>

			<!-- Календарь окон -->
			<div class="overflow-x-auto">
				<!-- Даты -->
				<div
					class="grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-4 text-center font-medium"
				>
					<div v-for="date in uniqueDates" :key="date">
						<div>{{ formatWeekday(date) }}</div>
						<div class="text-lg">{{ formatDate(date) }}</div>
					</div>
				</div>
				<!-- Слоты -->
				<div
					class="grid grid-cols-[repeat(auto-fit,minmax(150px,1fr))] gap-4 mt-4"
				>
					<div v-for="date in uniqueDates" :key="date" class="space-y-4">
						<div
							v-for="slot in byDate[date]"
							:key="slot.id"
							class="border p-3 rounded"
						>
							<div class="flex justify-between">
								<div>
									<div class="font-semibold">{{ slot.title }}</div>
									<div class="text-sm">
										{{ slot.start_time }}–{{ slot.end_time }}
									</div>
								</div>
								<button @click="toggle(slot.id)" class="text-blue-600 text-sm">
									{{
										opened === slot.id
											? '×'
											: `${slot.appointments.length}/${slot.max_slots}`
									}}
								</button>
							</div>
							<transition name="fade">
								<div v-if="opened === slot.id" class="mt-2 text-sm space-y-1">
									<div v-for="a in slot.appointments" :key="a.position">
										{{ a.position }}. {{ a.first_name }} {{ a.last_name }}
									</div>
									<div v-if="!slot.appointments.length" class="text-gray-500">
										Никто не записан
									</div>
								</div>
							</transition>
						</div>
					</div>
				</div>
			</div>
		</section>
	</div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
	transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
	opacity: 0;
}
</style>
