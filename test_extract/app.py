# app.py
import math
import random

def calculate_area(radius):
    area = 3.14 * radius ** 2
    print("Area:", area)
    return area

def divide(a,b):
    return a/b

def print_items():
    items=["A","B","C"]
    for i in range(len(items)+1):
        print(items[i])

def average(nums):
    total=0
    for n in nums:
        total+=n
    return total/len(nums)

def main():
    r=input("Radius: ")
    calculate_area(r)
    print(divide(10,0))
    print_items()
    print(average([]))
    print(math.sqr(25))

if __name__=="__main__":
    main()
