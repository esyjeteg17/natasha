<template>
	<section class="max-w-7xl mx-auto py-8 w-full">
		<h1 class="text-3xl font-semibold mb-8">Дисциплины</h1>
		<div>
			<div
				v-if="coursesStore.myCourses && coursesStore.myCourses"
				class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
			>
				<MyCourseItem
					v-if="coursesStore.myCourses"
					v-for="course in coursesStore.myCourses"
					:id="course.id"
					:title="course.title"
					:img="course.img"
					:description="course.description"
					:teacher="course.teacher"
					:date="course.date"
					:hours="course.hours"
				/>
				<p v-else class="text-center text-gray-500">
					Пока нет доступных курсов.
				</p>
			</div>
		</div>
	</section>
</template>

<script setup lang="ts">
interface Course {
	id: number
	title: string
	description: string
	hours: number
	teacher: string
	coverUrl?: string
}

const coursesStore = useCoursesStore()
const isAuthenticated = useAuthStore().isAuthenticated

onMounted(() => {
	if (!isAuthenticated) {
		navigateTo('/login')
	}
})
if (!coursesStore.myCourses.length) {
	await coursesStore.getMyCourses()
}
</script>

<style scoped>
.line-clamp-2 {
	display: -webkit-box;
	-webkit-line-clamp: 2;
	-webkit-box-orient: vertical;
	overflow: hidden;
}

.line-clamp-3 {
	display: -webkit-box;
	-webkit-line-clamp: 3;
	-webkit-box-orient: vertical;
	overflow: hidden;
}
</style>
