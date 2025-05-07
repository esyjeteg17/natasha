import type { Course } from '~/types'
import axios from 'axios'

export const useCoursesStore = defineStore('courses', () => {
	const courses = ref<Course[]>([])
	const myCourses = ref<Course[]>([])
	const currentCourse = ref<Course>()
	const currentTopics = ref([])

	const getCourses = async () => {
		try {
			const { data } = await axios.get('http://127.0.0.1:8000/api/courses/')
			courses.value = data as Course[]
		} catch (error) {
			console.error('Error fetching courses:', error)
		}
	}

	const getMyCourses = async (id?: number) => {
		try {
			const { data } = await axios.get(
				'http://127.0.0.1:8000/api/courses/',

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
				`http://127.0.0.1:8000/api/courses/${id}/`,

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
				`http://127.0.0.1:8000/api/topics/`,

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

	return {
		getMyCourses,
		getCourses,
		getCourse,
		getTopics,
		courses,
		myCourses,
		currentTopics,
	}
})
