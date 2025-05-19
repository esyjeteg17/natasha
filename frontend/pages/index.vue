<script setup lang="ts">
const q = ref('')
</script>

<template>
	<section class="pb-10 w-11/12 mx-auto max-w-7xl">
		<h1 class="text-3xl font-bold mt-10 mb-6">Наши лучшие курсы</h1>

		<div class="grid grid-cols-1 md:grid-cols-3 grid-rows-2 gap-5">
			<CourseItemMain
				class="md:col-span-2 md:row-span-2"
				:id="101"
				slug="vue-3"
				img="/img/courses/be3fbaaf1e6937c6a841c6ecff3d022b.jpg"
				title="Полный курс по Vue.js 3"
				teacher="Максим Петров"
				date="15 мар 2025"
			/>

			<CourseItemMain
				:id="102"
				slug="python"
				img="/img/courses/scale_1200.jpeg"
				title="Продвинутый Python для аналитиков"
				teacher="Наташа Котюшева"
				date="28 фев 2025"
			/>

			<CourseItemMain
				:id="103"
				slug="design"
				img="/img/courses/c92f97fd043da7423ec1940deef5b471_big.jpg"
				title="Основы графического дизайна"
				teacher="Анна Иванова"
				date="05 апр 2025"
			/>
		</div>
	</section>
</template>

<style scoped></style>
