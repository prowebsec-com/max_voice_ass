from src.core.brain import Brain

def test_brain():
    brain = Brain()
    
    # Test Greeting
    print("Testing Greeting...")
    resp = brain.think("hello")
    assert "Hey there" in resp
    print(f"PASS: {resp}")

    # Test Time
    print("\nTesting Time...")
    resp = brain.think("what time is it")
    assert "It's currently" in resp
    print(f"PASS: {resp}")

    # Test Calculator (Mocking subprocess would be better but checking string return is fine)
    print("\nTesting Open Calc...")
    resp = brain.think("open calculator")
    assert "Calculator" in resp
    print(f"PASS: {resp}")

    # Test Fallback/Wikipedia
    print("\nTesting Wikipedia (Online)...")
    resp = brain.think("who is albert einstein")
    if "Here's what I found" in resp:
        print(f"PASS: {resp}")
    else:
        print(f"WARN (Network might be down or query failed): {resp}")

    # Test Emotion
    print("\nTesting Emotion...")
    resp = brain.think("I am bored")
    assert "joke" in resp or "music" in resp
    print(f"PASS: {resp}")

if __name__ == "__main__":
    test_brain()
