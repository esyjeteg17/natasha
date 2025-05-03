import type { Course } from '~/types'
import axios from 'axios'

export const courses = defineStore('courses', () => {
	const courses = ref<Course[]>([])

	const getCourses = async () => {
		try {
			const { data } = await axios.get('http://127.0.0.1:8000/api/courses/')
			courses.value = data as Course[]
		} catch (error) {
			console.error('Error fetching courses:', error)
		}
	}
	return { courses }
})
