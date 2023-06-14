from numpy import random as rd
import random

names = ["Corey", "John", "Neill", "Linda", "Becky", "Jamie"]

with open("test_data/test_data.csv", "w") as file:
    file.write("name,score,age_category,email,phone_num\n")
    
    for i in range(len(names)):
        name = rd.choice(names, replace=False)
        names.pop(names.index(name))
        score = random.randint(1,30)
        email = f"{name}@domain.com"
        phone_num = random.randint(1000000,9999999)
        
        file.write(f"{name},{score},Senior,{email},{phone_num}\n")