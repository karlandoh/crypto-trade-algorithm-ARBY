import os

folder_1 = f"{os.getcwd()}/currenttrades"

for file in os.listdir(folder_1):
	with open(f"{folder_1}/{file}", "r") as text_file:
		text_file.seek(0)
		data = text_file.read()
		text_file.close()

	

	#if 'mandala' in str(data):
	#	print(file)
	#continue

	with open(f"{folder_1}/{file}", "w") as text_file:
		text_file.seek(0)
		data = text_file.write(data.replace("ccxt.hitbtc2()","ccxt.hitbtc()"))
		text_file.close()

	print(f"Replaced {folder_1}/{file}")