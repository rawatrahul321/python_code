def combination_sum(candidates, target):
    def backtrack(start, target, path, result):
        if target == 0:
            result.append(path[:])
            # print(result,"resulttttttttt")
            return
        for i in range(start, len(candidates)):
            if candidates[i] > target:
                print(path,candidates[i],target)
                continue
            path.append(candidates[i])
            print(path,"First Path")
            backtrack(i, target - candidates[i], path, result)
            path.pop()
            # print(path,"After Path Pop",target)
    result = []
    candidates.sort()
    backtrack(0, target, [], result)
    return result
candidates = [2, 3, 5]
target = 8
print(combination_sum(candidates, target))
