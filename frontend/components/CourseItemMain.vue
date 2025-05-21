<template>
	<NuxtLink
		:to="`/courses/${slug}`"
		class="block relative overflow-hidden rounded-lg shadow-lg group"
	>
		<!-- Изображение -->
		<img
			:src="img"
			:alt="title"
			class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
		/>

		<!-- Градиентный оверлей и текст -->
		<div
			class="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent"
		/>

		<div class="absolute bottom-0 left-0 p-6 text-white">
			<span
				class="inline-block bg-black/60 px-3 py-1 rounded-full text-xs mb-2"
			>
				{{ teacher }}
			</span>
			<h2 class="text-xl font-semibold leading-tight">{{ title }}</h2>
			<p class="text-sm mt-1 opacity-80">{{ date }}</p>
		</div>
	</NuxtLink>
</template>

<script setup lang="ts">
const props = defineProps<{
	id: number
	img: string
	title: string
	teacher: string
	date: string
	slug: string
}>()
</script>
