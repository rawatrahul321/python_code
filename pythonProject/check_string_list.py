# word1 = ["a", "cb"]
# word2 = ["ab", "c"]
word1 = ["ab", "c"]
word2 = ["a", "bc"]
def check_string(word1,word2):
    print(''.join(word1),''.join(word2))
    return "".join(word1)=="".join(word2)
print(check_string(word1,word2))
