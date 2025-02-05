def wordPattern(pattern,s):
    words = s.split()
    char_to_word = {}
    word_to_char = {}
    for char,word in zip(pattern,words):
        if char not in char_to_word and word not in word_to_char:
            char_to_word[char] = word 
            word_to_char[word] = char
        elif char_to_word.get(char)!= word and word_to_char.get(word)!=char:
            return False
    return True
    print(char_to_word)
    print(word_to_char)
    
print(wordPattern("abba", "dog cat cat dog"))  # True
print(wordPattern("abba", "dog cat cat fish"))  # False
print(wordPattern("aaaa", "dog cat cat dog"))  # False