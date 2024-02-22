import random
from dataclasses import dataclass

@dataclass
class Persona:
    profile: str
    mood: str
    tone: str

def create_persona() -> Persona:
    """Defines the persona of the user interacting with Einstein, focusing on those interested in mathematics."""
    profiles = [
        "math enthusiast",
        "math student",
        "research mathematician",
        "math teacher",
        "theoretical physicist",
        "engineer",
        "student",
        "teacher",
        "researcher",
        "physicist",
        "scientist",
        "mathematician",
        "data scientist",
        "math tutor",
        "math hobbyist",
        "data analyst",
        "data engineer",
        "data enthusiast",
        "data student",
        "data teacher",
        "data researcher"
    ]

    mood = [
        "curious",
        "puzzled",
        "eager",
        "analytical",
        "determined",
        "excited",
    ]

    tone = [
        "inquisitive",
        "thoughtful",
        "meticulous",
        "enthusiastic",
        "serious",
        "playful",
    ]

    return Persona(
        profile=random.choice(profiles),
        mood=random.choice(mood),
        tone=random.choice(tone),
    )
