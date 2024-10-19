def word_frequency(text):
    word_count = {}
    words = text.split()

    for word in words:
        word_count[word] = word_count.get(word, 0) + 1

    sorted_word_count = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

    for word, count in sorted_word_count:
        print(f"{word} {count}")

# Example usage:
text = "the day is sunny the the sunny is is"
word_frequency(text)
