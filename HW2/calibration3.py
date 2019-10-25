import os.path
from os import path
from timeit import default_timer as timer

def calculate_factorial():
    factorial = 1

    for i in range(2, 300000):
        factorial *= i
    return factorial

if path.exists("calibration.txt"):
     os.remove("calibration.txt")
output_f = open("calibration.txt", 'w')

start_first_iter = timer()
calculate_factorial()
end_first_iter = timer()

start_second_iter = timer()
calculate_factorial()
end_second_iter = timer()

start_third_iter = timer()
calculate_factorial()
end_third_iter = timer()

average_time = ((end_first_iter - start_first_iter) + (end_second_iter - start_second_iter) + (end_third_iter - start_third_iter)) / 3
# Best avg performing time in Macbook Pro 2015 15 inch Max Specs
ratio = 42.83 / average_time

# print(str(average_time))
# print(str(ratio))

output_f.write(str(ratio))
output_f.close()
