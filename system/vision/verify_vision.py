from system.red_vision import RedVision

vision = RedVision()

print("Red is looking at your screen...")
result = vision.analyze_screen("What is currently visible on the primary monitor? Just give me a Gen Z vibe summary.")

print(f"Red's Perception: {result}")
