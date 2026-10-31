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
# Generate content hooks
print("\n========== CONTENT HOOK GENERATOR ==========")

hooks = [
    f"Nobody talks enough about {topic}. Let's discuss!",
    f"If you're part of {audience}, this is for you!",
    f"Let's be honest: we need to talk about {topic}."
]

for number, hook in enumerate(hooks, start=1):
    print(f"HOOK {number}: {hook}")

# Generate a caption
print("\n========== SUGGESTED CAPTION ==========")

caption = f"""
Let's talk about {topic}!

This one is for {audience}.

Whether you are learning, experiencing it
or simply curious, there's something here
worth discussing.

What do you think? Share your thoughts
in the comments!

#YamayaAfrique #NigerianYouth #YouthCulture
"""

print(caption)

print("Your content suggestions are ready!")
