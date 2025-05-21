<script setup lang="ts">
const username = ref('')
const password = ref('')
const email = ref('')
const firstName = ref('')
const lastName = ref('')
const role = ref('student')

const authStore = useAuthStore()

async function onRegister() {
	try {
		const resp: any = await $fetch('https://uchebnyicourse-k-n.ru/api/users/', {
			method: 'POST',
			body: {
				username: username.value,
				password: password.value,
				email: email.value,
				first_name: firstName.value,
				last_name: lastName.value,
				role: role.value,
			},
		})
		if (resp?.id) {
			await authStore.login(username.value, password.value)
			if (authStore.isAuthenticated) {
				return navigateTo('/')
			}
		}
	} catch (error: any) {
		console.error('Ошибка регистрации', error)
	}
}
</script>

<template>
	<section class="my-12 text-gray-800">
		<div class="max-w-sm mx-auto bg-gray-50 p-6 rounded-md shadow-md">
			<h1 class="text-xl font-bold mb-5 text-center">Регистрация</h1>

			<form @submit.prevent="onRegister">
				<div class="flex flex-col mb-4">
					<input
						type="email"
						v-model="email"
						placeholder="Email"
						required
						class="w-full mb-3 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
					/>

					<input
						type="text"
						placeholder="Имя пользователя"
						v-model="username"
						required
						class="w-full mb-3 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
					/>

					<input
						type="text"
						placeholder="Имя"
						v-model="firstName"
						required
						class="w-full mb-3 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
					/>

					<input
						type="text"
						placeholder="Фамилия"
						v-model="lastName"
						required
						class="w-full mb-3 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
					/>

					<input
						type="password"
						v-model="password"
						placeholder="Пароль"
						required
						class="w-full mb-3 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
					/>

					<input
						type="password"
						placeholder="Повторите пароль"
						required
						class="w-full mb-3 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
					/>
				</div>

				<button
					type="submit"
					class="w-full py-2 bg-gray-800 text-white rounded-md font-semibold hover:bg-purple-700 transition-colors"
				>
					Зарегистрироваться
				</button>
			</form>
		</div>
	</section>
</template>
