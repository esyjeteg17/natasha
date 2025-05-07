<script setup lang="ts">
import { NuxtLink } from '#components'

const authStore = useAuthStore()
const router = useRouter()

const isAuthenticated = computed(() => authStore.isAuthenticated)

const fullName = computed(() => {
	if (!authStore.user) return ''
	return `${authStore.user.first_name} ${authStore.user.last_name}`
})

function logout() {
	authStore.logout()
	router.push({ name: 'index' })
}
</script>

<template>
	<div class="container mx-auto mb-10">
		<header class="flex items-center justify-between py-3">
			<!-- Logo -->
			<NuxtLink :to="{ name: 'index' }" class="flex items-center font-bold">
				<p>Учебный портал</p>
				<img src="/img/icons/logo.svg" alt="Logo" class="ml-2" />
			</NuxtLink>

			<!-- Search -->
			<div class="relative w-[305px]">
				<form action="#" method="get" class="relative">
					<button
						type="submit"
						class="absolute left-4 top-1/2 -translate-y-1/2 w-6 h-6 bg-[url('/img/icons/search_icon.svg')] bg-no-repeat bg-cover border-none outline-none"
					></button>
					<input
						type="text"
						name="q"
						placeholder="Найти курсы"
						class="pl-12 w-full h-12 rounded-full border border-gray-700 focus:outline-none"
					/>
				</form>
			</div>

			<!-- Navigation -->
			<nav>
				<ul class="flex space-x-5 text-sm">
					<li><NuxtLink :to="{ name: 'my-courses' }">Дисциплины</NuxtLink></li>
					<li><a href="#">Расписание</a></li>
					<!-- <li><a href="#">Тестирование</a></li> -->
				</ul>
			</nav>

			<!-- Auth -->
			<div>
				<!-- Если НЕ авторизован: показываем кнопки Войти / Регистрация -->
				<div v-if="!isAuthenticated">
					<NuxtLink
						:to="{ name: 'login' }"
						class="inline-block mr-5 py-2 px-4 border border-gray-800 font-bold text-gray-800 hover:bg-gray-800 hover:text-white transition-colors"
					>
						Войти
					</NuxtLink>
					<NuxtLink
						:to="{ name: 'register' }"
						class="inline-block py-2 px-4 border border-gray-800 bg-gray-800 text-white font-bold hover:bg-white hover:text-gray-800 transition-colors"
					>
						Регистрация
					</NuxtLink>
				</div>

				<div v-else class="flex items-center space-x-4 h-full">
					<NuxtLink :to="{ name: 'profile' }" class="font-bold">
						{{ fullName }}
					</NuxtLink>
					<button
						@click="logout"
						class="inline-block py-2 px-4 border border-gray-800 font-bold text-gray-800 hover:bg-gray-800 hover:text-white transition-colors"
					>
						Выйти
					</button>
					<NuxtLink
						v-if="authStore.user?.role === 'teacher'"
						:to="{
							name: 'courses-create',
						}"
						class="h-full p-3 flex items-center justify-center border border-gray-800 font-bold text-gray-800 hover:bg-gray-800 hover:text-white transition-colors"
					>
						<IconsPlus />
					</NuxtLink>
				</div>
			</div>
		</header>
	</div>
</template>
