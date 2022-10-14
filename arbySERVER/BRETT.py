

def student(*args, **kwargs):
	print(info['age'])

	#print(kwargs)


courses = ["Math", "Gym", "CS"]
info = {"name": "tyco", "age": 19}
student(*courses, **info)

# print(list("brett"))

#student(" naruto", "sasuke", name="Uchiha")