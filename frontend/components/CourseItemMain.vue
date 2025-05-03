<script setup lang="ts">
const authStore = useAuthStore()

const props = defineProps({
	id: Number,
	img: String,
	title: String,
	teacher: String,
	date: String,
})
</script>

<template>
	<div>
		<NuxtLink :to="{ name: 'courses-id', params: { id: props.id } }">
			<img :src="props.img" :alt="props.title" class="w-full h-auto block" />
			<div class="absolute bottom-5 left-2 text-white p-2 box-border">
				<span class="inline-block bg-[#2D2F31] py-2 px-6 mb-2">{{
					props.teacher
				}}</span>
				<h2 class="text-xl font-bold m-0">{{ props.title }}</h2>
				<p class="text-sm mt-1">{{ props.date }}</p>
			</div>
		</NuxtLink>
	</div>
</template>
