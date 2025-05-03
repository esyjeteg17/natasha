<script setup lang="ts">
const authStore = useAuthStore()

const checkAuth = () => {
	if (!authStore.user) {
		return navigateTo('/login')
	} else {
		return
	}
}
checkAuth()
</script>

<template>
	<div class="max-w-screen-xl mx-auto px-4 py-8">
		<section class="w-full border border-gray-200 p-6 bg-white rounded-md">
			<div class="text-2xl font-normal mb-5">
				Информация о
				{{ authStore.user?.role === 'student' ? 'студенте' : 'преподавателе' }}
			</div>

			<div class="flex justify-between items-start gap-10">
				<div class="w-[250px] h-[250px] flex-shrink-0">
					<img
						src="/img/profile.png"
						alt="Profile Image"
						class="w-full h-full object-cover"
					/>
				</div>

				<div class="w-[920px]">
					<div
						class="text-xl font-medium text-gray-500 border-b border-gray-200 pb-3 mb-8"
					>
						{{ authStore.user?.first_name }} {{ authStore.user?.last_name }}
					</div>

					<div class="flex justify-between h-full">
						<div>
							<ul>
								<li class="flex items-center mb-5 text-blue-900 font-light">
									<span class="mr-2 px-4 py-3 bg-blue-600 text-white text-base"
										>0</span
									>
									Лабораторные на проверке
								</li>
								<li class="flex items-center mb-5 text-blue-900 font-light">
									<span class="mr-2 px-4 py-3 bg-blue-600 text-white text-base"
										>0</span
									>
									Лабораторные на проверке
								</li>
								<li class="flex items-center mb-5 text-blue-900 font-light">
									<span class="mr-2 px-4 py-3 bg-blue-600 text-white text-base"
										>0</span
									>
									Лабораторные на проверке
								</li>
							</ul>
						</div>

						<div class="pr-20">
							<ul class="mb-6">
								<li class="mb-4 text-gray-500">
									Адрес электронной почты:
									<span class="text-blue-900">{{ authStore.user?.email }}</span>
								</li>
								<li class="mb-4 text-gray-500">
									Номер телефона:
									<span class="text-blue-900">{{
										authStore.user?.phone ? authStore.user?.phone : 'Не указан'
									}}</span>
								</li>
								<li class="mb-4 text-gray-500">
									Учебная группа:
									<span class="text-blue-900">{{
										authStore.user?.group ? authStore.user?.group : 'Не указана'
									}}</span>
								</li>
							</ul>
							<a
								href="#"
								class="inline-block bg-gray-900 text-white px-4 py-2 font-light rounded hover:bg-gray-700 transition-colors"
							>
								Редактировать данные
							</a>
						</div>
					</div>
				</div>
			</div>
		</section>
	</div>
</template>

<style scoped></style>
