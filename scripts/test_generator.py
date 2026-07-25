from generator import Generator


generator = Generator()

chunks = [
    {
        "text": "According to NCAA rules, a false start occurs when a competitor begins a start motion before the starting signal.",
        "metadata": {
            "source": "NCAA Rule Book"
        }
    }
]


answer = generator.generate_answer(
    "What is a false start?",
    chunks
)


print(answer)
