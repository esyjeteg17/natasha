<script setup lang="ts">
const props = defineProps<{
	id: number
	img?: string
	description?: string
	title: string
	teacher: any
	date: string
	hours: number
}>()
</script>

<template>
	<div>
		<NuxtLink :key="id" :to="`/courses/${props.id}`" class="group">
			<div
				class="bg-white rounded-2xl shadow-md overflow-hidden transition-transform duration-300 group-hover:-translate-y-1"
			>
				<img v-if="img" :src="img" alt="" class="h-40 w-full object-cover" />

				<div class="p-4">
					<h2 class="text-xl font-medium mb-2 line-clamp-2">
						{{ title }}
					</h2>
					<p class="text-sm text-gray-600 mb-4 line-clamp-3">
						{{ description }}
					</p>
					<div class="flex justify-between text-sm text-gray-500">
						<span>{{ hours }} ч</span>
						<span>{{ teacher?.first_name }} {{ teacher?.last_name }}</span>
					</div>
				</div>
			</div>
		</NuxtLink>
	</div>
</template>
