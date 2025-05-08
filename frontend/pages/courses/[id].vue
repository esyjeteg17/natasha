<script setup lang="ts">
import { NuxtLink } from '#components'

const coursesStore = useCoursesStore()
const isAuthenticated = useAuthStore().isAuthenticated

const route = useRoute()
const { id } = route.params

if (!isAuthenticated) {
	navigateTo('/login')
}

await Promise.all([
	coursesStore.getCourse(+id),
	coursesStore.getTopics(+id),
	coursesStore.getTasks(),
])

const tabs = ['Курс', 'Участники', 'Оценки', 'Компетенции']
const activeTab = ref('Курс')

const sections = computed(() => {
	return coursesStore.currentTopics
		.filter(item => item.course === +id)
		.map(item => {
			return {
				title: item.title,
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

function getIconComponent(type: string) {
	switch (type) {
		case 'video':
			return {
				template:
					'<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M4 6h9a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
			}
		case 'pdf':
			return {
				template:
					'<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 ... Z" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
			}
		default:
			return {
				template:
					'<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 12h8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
			}
	}
}
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
					Мои курсы
				</NuxtLink>
			</div>
		</div>

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
			<div v-for="section in sections" :key="section.title" class="mb-6">
				<button
					class="w-full flex justify-between items-center bg-gray-100 p-4 rounded-t-md focus:outline-none"
					@click="toggleSection(section.title)"
				>
					<span class="font-medium text-lg">{{ section.title }}</span>

					<span>
						<svg
							v-if="openSections.includes(section.title)"
							class="w-5 h-5 text-gray-600 transform rotate-180"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 9l-7 7-7-7"
							/>
						</svg>
						<svg
							v-else
							class="w-5 h-5 text-gray-600"
							fill="none"
							stroke="currentColor"
							viewBox="0 0 24 24"
						>
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M19 9l-7 7-7-7"
							/>
						</svg>
					</span>
				</button>
				<div
					v-show="openSections.includes(section.title)"
					class="border border-t-0 border-gray-200 p-4 rounded-b-md"
				>
					<ul>
						<li
							v-for="item in section.items"
							:key="item.id"
							class="flex items-center justify-between p-4 border-b last:border-b-0"
						>
							<div class="flex items-center space-x-4">
								<component
									:is="getIconComponent(item.type)"
									class="w-8 h-8 text-blue-600"
								/>
								<div>
									<NuxtLink :to="`/tasks/${item.id}`" class="font-medium">{{
										item.title
									}}</NuxtLink>
								</div>
							</div>
							<button
								class="px-3 py-1 border rounded focus:outline-none"
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
				</div>
			</div>
		</div>

		<!-- Placeholder for other tabs -->
		<div v-else class="p-4 text-gray-500">
			Содержание раздела «{{ activeTab }}» пока не реализовано.
		</div>
	</div>
</template>
