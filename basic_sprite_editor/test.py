test_art = \
[
    [0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0]
]

def printart(test_art):
    for i in range(8):
        for j in range(8):
            if test_art[i][j] == 1:
                print('*', end='')
            else:
                print('_', end='')
        print()

flipped = [[test_art[i][j] for j in range(len(test_art[i])-1, -1, -1)] for i in range(len(test_art)-1, -1, -1)]

printart(test_art)
print()
printart(flipped)