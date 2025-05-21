<script setup lang="ts">
const authStore = useAuthStore()
const router = useRouter()

// Redirect if not authenticated
onMounted(() => {
	if (!authStore.user) router.push('/login')
})

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

// Режим редактирования
const editMode = ref(false)

// Локальная копия полей профиля
const form = reactive({
	first_name: '',
	last_name: '',
	email: '',
	phone: '',
})

function startEdit() {
	if (!authStore.user) return
	editMode.value = true
	// заполняем форму текущими данными
	form.first_name = authStore.user.first_name || ''
	form.last_name = authStore.user.last_name || ''
	form.email = authStore.user.email || ''
	form.phone = authStore.user.phone || ''
}

function cancelEdit() {
	editMode.value = false
}

// Сохраняем изменения
async function saveProfile() {
	if (!authStore.user) return
	try {
		const updated = await $fetch(`/api/users/${authStore.user.id}/`, {
			baseURL: authStore.baseURL,
			method: 'PATCH',
			headers: { Authorization: `Bearer ${authStore.accessToken}` },
			body: {
				first_name: form.first_name,
				last_name: form.last_name,
				email: form.email,
				phone: form.phone,
			},
		})
		authStore.user = updated
		editMode.value = false
	} catch (e: any) {
		console.error('Ошибка при сохранении профиля', e)
		alert('Не удалось сохранить: ' + (e.data?.detail || e.message))
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
						<div>
							<img
								src="/img/profile.png"
								alt="Profile"
								class="w-full h-full object-cover rounded-lg"
							/>
						</div>
						<div class="col-span-2 space-y-6">
							<template v-if="!editMode">
								<p>
									<span class="font-medium">Имя:</span>
									{{ authStore.user?.first_name }}
								</p>
								<p>
									<span class="font-medium">Фамилия:</span>
									{{ authStore.user?.last_name }}
								</p>
								<p>
									<span class="font-medium">Email: </span>
									<a
										:href="`mailto:${authStore.user?.email}`"
										class="text-blue-600 hover:underline"
									>
										{{ authStore.user?.email }}
									</a>
								</p>
								<p>
									<span class="font-medium">Телефон:</span>
									{{ authStore.user?.phone || 'Не указан' }}
								</p>
								<button
									@click="startEdit"
									class="mt-4 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
								>
									Редактировать данные
								</button>
							</template>

							<template v-else>
								<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
									<div>
										<label class="block text-sm font-medium mb-1">Имя</label>
										<input
											v-model="form.first_name"
											type="text"
											class="w-full border px-3 py-2 rounded"
										/>
									</div>
									<div>
										<label class="block text-sm font-medium mb-1"
											>Фамилия</label
										>
										<input
											v-model="form.last_name"
											type="text"
											class="w-full border px-3 py-2 rounded"
										/>
									</div>
									<div>
										<label class="block text-sm font-medium mb-1">Email</label>
										<input
											v-model="form.email"
											type="email"
											class="w-full border px-3 py-2 rounded"
										/>
									</div>
									<div>
										<label class="block text-sm font-medium mb-1"
											>Телефон</label
										>
										<input
											v-model="form.phone"
											type="text"
											class="w-full border px-3 py-2 rounded"
										/>
									</div>
								</div>
								<div class="mt-4 flex gap-2">
									<button
										@click="saveProfile"
										class="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 transition"
									>
										Сохранить
									</button>
									<button
										@click="cancelEdit"
										class="bg-gray-300 text-gray-800 px-6 py-2 rounded hover:bg-gray-400 transition"
									>
										Отмена
									</button>
								</div>
							</template>
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
