<script setup lang="ts">
const username = ref('')
const password = ref('')

const authStore = useAuthStore()

async function onSubmit() {
	try {
		await authStore.login(username.value, password.value)
		navigateTo('/')
	} catch (error: any) {
		alert(error.message)
	}
}
</script>

<template>
	<section class="flex items-center justify-center h-screen bg-gray-100">
		<div class="w-full max-w-md bg-white p-8 shadow-md rounded-md">
			<h1 class="text-2xl font-bold text-gray-800 mb-6 text-center">
				Вход в учетную запись
			</h1>

			<form @submit.prevent="onSubmit">
				<div class="mb-4">
					<label
						for="email"
						class="block text-sm font-medium text-gray-700 mb-1"
					>
						Username
					</label>
					<input
						id="email"
						type="text"
						v-model="username"
						required
						class="w-full border border-gray-300 rounded-md py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
					/>
				</div>
				<div class="mb-4">
					<label
						for="password"
						class="block text-sm font-medium text-gray-700 mb-1"
					>
						Пароль
					</label>
					<input
						id="password"
						type="password"
						v-model="password"
						required
						class="w-full border border-gray-300 rounded-md py-2 px-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
					/>
				</div>
				<button
					type="submit"
					class="w-full py-2 bg-gray-800 text-white rounded-md text-base font-bold hover:bg-purple-700 transition-colors"
				>
					Войти
				</button>
			</form>

			<div class="mt-4 text-sm text-center">
				<p>
					У вас еще нет учетной записи?
					<NuxtLink to="/register" class="text-blue-500 hover:underline">
						Зарегистрироваться
					</NuxtLink>
				</p>
			</div>
		</div>
	</section>
</template>
