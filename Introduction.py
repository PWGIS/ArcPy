# Use the arguments provided to create an output
# identical to the ones created in the previous exercise
# ERIKA:  2106
# Jason: Erika & Miguel & Jason & Sean
# Sean:  GIS Coordinator & GIS Tech II & GIS Analyst & GIS Technician I
# Miguel: 2048131332

MTName = "Miguel"
EEName = "Erika"
SDName = "Sean"
JBName = "Jason"

MTTitle = "GIS Technician I"
JBTitle = "GIS Analyst"
SDTitle = "GIS Coordinator"
EETitle = "GIS Tech II"

JBNum = "13"
MTNum = "2048"
EENum = "13"
SDNum = "32"

print MTNum + JBNum + EENum + SDNum
Number = int(JBNum) + int(MTNum) + int(EENum) + int(SDNum)
print "Here's the number:"
print Number






























from turtle import *      # use the turtle library
space = Screen()          # create a turtle screen (space)
bob = Turtle()            # create a turtle named bob

# Make a square
bob.forward(100)          # tell bob to move forward by 100 units
bob.right(90)             # turn right by 90 degrees
bob.forward(100)          # tell bob to move forward by 100 units
bob.right(90)             # turn right by 90 degrees
bob.forward(100)          # tell bob to move forward by 100 units
bob.right(90)             # turn right by 90 degrees
bob.forward(100)          # tell bob to move forward by 100 units

# Position for roof
bob.right(90)

# Make a roof
bob.forward(100)          # tell bob to move forward by 100 units
bob.right(-120)           # turn LEFT by 120 degrees
bob.forward(100)          # tell bob to move forward by 100 units
bob.right(-120)           # turn LEFT by 120 degrees
bob.forward(100)          # tell bob to move forward by 100 units
bob.right(-120)           # turn LEFT by 120 degrees


print "And I made you a house you're welcome."
