<script setup lang="ts">
const q = ref('')
</script>

<template>
	<section class="py-10">
		<div class="max-w-7xl mx-auto">
			<h1 class="text-3xl font-bold mt-10 mb-6">Наши Лучшие курсы</h1>
		</div>

		<div
			class="max-w-7xl mx-auto grid gap-5"
			style="grid-template-columns: 2fr 1fr; grid-template-rows: repeat(2, 1fr)"
		>
			<CourseItemMain
				style="grid-column: 1 / 2; grid-row: 1 / 3"
				class="relative"
				:id="5"
				img="/img/courses/course_1.png"
				title="Название первого курса"
				teacher="Категория 1"
				date="01 Мар 2024"
			/>

			<CourseItemMain
				style="grid-column: 2 / 3; grid-row: 1 / 2"
				class="relative"
				:id="3"
				img="/img/courses/course_1.png"
				title="Название второго курса"
				teacher="Категория 2"
				date="13 Мар 2024"
			/>

			<CourseItemMain
				style="grid-column: 2 / 3; grid-row: 2 / 3"
				class="relative"
				:id="2"
				img="/img/courses/course_1.png"
				title="Название третьего курса"
				teacher="Категория 3"
				date="25 Май 2024"
			/>
		</div>
	</section>
</template>

<style scoped></style>
