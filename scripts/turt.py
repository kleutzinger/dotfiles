import turtle
import random
kev = turtle.Turtle()
jada = turtle.Turtle()

kev.pencolor('black')
jada.pencolor('#9400D3')

pensize = 2

kev.pensize(pensize)
jada.pensize(pensize)
jada.hideturtle()
kev.hideturtle()
speed = 0
kev.speed(speed)
jada.speed(speed)

# this is a comment, not code
# i love you jada cooks

# kev.left(1)
# jada.right(5)
# kev.fd(5)

def rand_color():
    return [random.random() for _ in range(3)]

random.seed(2)

for dist in range(2000):
    # kev.pencolor(rand_color())
    # kev.fd(dist)
    jada.fd(dist/2)
    jada.pencolor('black')
    # jada.circle(dist / 2.5)
    jada.pencolor('pink')
    jada.dot(dist)
    jada.pencolor('black')
    jada.circle(dist)
    # kev.left(random.choice([45, -45, 90, -90, 0]))
    jada.left(15)
import time
time.sleep(5)