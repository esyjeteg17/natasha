import type { Course } from '~/types'
import axios from 'axios'

export const useCoursesStore = defineStore('courses', () => {
	const courses = ref<Course[]>([])
	const myCourses = ref<Course[]>([])
	const currentCourse = ref<Course>()
	const currentTopics = ref([])
	const currentTasks = ref([])

	const getCourses = async () => {
		try {
			const { data } = await axios.get(
				'https://uchebnyicourse-k-n.ru/api/courses/'
			)
			courses.value = data as Course[]
		} catch (error) {
			console.error('Error fetching courses:', error)
		}
	}

	const getMyCourses = async (id?: number) => {
		try {
			const { data } = await axios.get(
				'https://uchebnyicourse-k-n.ru/api/courses/',

				{
					params: { id: id },
					headers: {
						Authorization: `Bearer ${useAuthStore().accessToken}`,
					},
				}
			)
			myCourses.value = data as Course[]
		} catch (error) {
			console.error('Error fetching my courses:', error)
		}
	}

	const getCourse = async (id?: number) => {
		try {
			const { data } = await axios.get(
				`https://uchebnyicourse-k-n.ru/api/courses/${id}/`,

				{
					headers: {
						Authorization: `Bearer ${useAuthStore().accessToken}`,
					},
				}
			)
			currentCourse.value = data as Course
		} catch (error) {
			console.error('Error fetching my courses:', error)
		}
	}

	const getTopics = async (id?: number) => {
		try {
			const { data } = await axios.get(
				`https://uchebnyicourse-k-n.ru/api/topics/`,

				{
					headers: {
						Authorization: `Bearer ${useAuthStore().accessToken}`,
					},
				}
			)
			currentTopics.value = data
		} catch (error) {
			console.error('Error fetching my courses:', error)
		}
	}

	const getTasks = async (id?: number) => {
		try {
			const { data } = await axios.get(
				`https://uchebnyicourse-k-n.ru/api/tasks/`,

				{
					headers: {
						Authorization: `Bearer ${useAuthStore().accessToken}`,
					},
				}
			)
			currentTasks.value = data
		} catch (error) {
			console.error('Error fetching my courses:', error)
		}
	}

	return {
		getMyCourses,
		getCourses,
		getCourse,
		getTopics,
		getTasks,
		courses,
		myCourses,
		currentTopics,
		currentCourse,
		currentTasks,
	}
})
