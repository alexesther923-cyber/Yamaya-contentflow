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
# Generate hooks based on selected tone
print("\n========== CONTENT HOOK GENERATOR ==========")

if "funny" in tone.lower() or "relatable" in tone.lower():
    hooks = [
        f"Can we talk about {topic} for a minute?",
        f"If you're a {audience}, you will understand this!",
        f"Why is nobody talking about {topic}?"
    ]

elif "educational" in tone.lower():
    hooks = [
        f"Here are 3 things to know about {topic}.",
        f"Let's break down everything about {topic}.",
        f"What you should understand about {topic}."
    ]

elif "professional" in tone.lower():
    hooks = [
        f"Understanding the importance of {topic}.",
        f"What you need to know about {topic}.",
        f"A closer look at {topic}."
    ]

else:
    hooks = [
        f"Let's explore {topic}.",
        f"Here's something worth knowing about {topic}.",
        f"Have you thought about {topic}?"
    ]

for number, hook in enumerate(hooks, start=1):
    print(f"HOOK {number}: {hook}")


# Generate a caption based on content format
print("\n========== SUGGESTED CAPTION ==========")

if "carousel" in format_type.lower():
    call_to_action = "Swipe through, save this post and share your thoughts!"

elif "reel" in format_type.lower():
    call_to_action = "Watch, share and tag someone who needs to see this!"

else:
    call_to_action = "Share your thoughts in the comments!"

caption = f"""
Let's talk about {topic}!

This one is for {audience}.

{call_to_action}

#YamayaAfrique #NigerianYouth #YouthCulture
"""

print(caption)

print("Your content suggestions are ready!")
