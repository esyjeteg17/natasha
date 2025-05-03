<script setup lang="ts">
const q = ref('')
</script>

<template>
	<!-- 	<input
		type="text"
		v-model="q"
		class="border border-gray-300 h-10 w-11/12 mx-auto rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
	/>
	<div class="mt-10 text-xl font-bold">{{ q }}</div> -->
	<section class="py-10">
		<div class="max-w-[1220px] mx-auto">
			<h1 class="text-3xl font-bold mt-10 mb-6">Наши Лучшие курсы</h1>
		</div>

		<div
			class="max-w-[1220px] mx-auto grid gap-5"
			style="grid-template-columns: 2fr 1fr; grid-template-rows: repeat(2, 1fr)"
		>
			<CourseItemMain
				style="grid-column: 1 / 2; grid-row: 1 / 3"
				class="relative"
				:id="5"
				img="/img/courses/course_1.png"
				title="Название dnjhjuj курса"
				teacher="Категория 3"
				date="01 Мар 2024"
			/>

			<CourseItemMain
				style="grid-column: 2 / 3; grid-row: 1 / 2"
				class="relative"
				:id="3"
				img="/img/courses/course_1.png"
				title="Название dnjhjuj курса"
				teacher="Категория 3"
				date="01 Мар 2024"
			/>

			<CourseItemMain
				style="grid-column: 2 / 3; grid-row: 2 / 3"
				class="relative"
				:id="2"
				img="/img/courses/course_1.png"
				title="Название третьего курса"
				teacher="Категория 3"
				date="01 Мар 2024"
			/>
		</div>
	</section>
</template>

<style scoped></style>
