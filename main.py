# YAMAYA CONTENTFLOW
# My first Python Project 
print("Welcome to Yamaya ContentFlow!") 
print("Your AI assisted content planning assistant")
# collect information from the user 
topic  = input("Enter your content topic")
audience = input("Who is your target audience? ")
format_type = input("What content format do you want? ")
tone = input("What tone should the content have?")
# Generate a simple content brief
print("\n========== YOUR CONTENT BRIEF ==========")
print("TOPIC:", topic)
print("TARGET AUDIENCE:", audience)
print("CONTENT FORMAT:", format_type)
print("TONE:", tone)
print("\nSUGGESTED CONTENT ANGLES:")

angles = [
    "An educational and informative approach",
    "A relatable, everyday experience",
    "A humorous or entertaining perspective"
]
for number, angle in enumerate(angles, start=1):
    print(f"{number}. {angle}")

print("\nCONTENT CHECKLIST:")
print("- Confirm the accuracy of information")
print("- Make sure the content suits the audience")
print("- Review the hook and main message")
print("- Check the call to action")

print("\nYour first content brief is ready!")
