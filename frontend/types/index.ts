export interface UserData {
	id: number
	username: string
	email: string
	role: string
	first_name: string
	last_name: string
	phone: string
	group: string
	course: string
}

export interface Course {
	id: number
	title: string
	description: string
	hours: number
	img?: string
	teacher: string
	date: string
	info_file: string
}
