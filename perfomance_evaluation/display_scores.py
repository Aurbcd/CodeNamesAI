score = open("score.txt", "r")
lines = list(map(int,score.readlines()))
print("Performance ratio:", len([i for i in lines if i==1])/len(lines), "win rate")
