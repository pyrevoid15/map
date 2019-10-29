import pygame
import random
import sys
import math

VIEWSCALE = 3
TILESCALE = 15


def get_distance(startpoint, endpoint):
    return math.sqrt((startpoint[0] - endpoint[0]) ** 2 + (startpoint[1] - endpoint[1]) ** 2)

def startup():
    w = World()

class Human:
    def __init__(self, position, occupation='unemployed', parents=(None, None)):
        self.position = position
        self.parents = [parents[0], parents[1]]
        self.gender = random.choice(['male', 'female'])
        self.energy = 1000

        if self.parents[0] is not None and self.parents[1] is not None:
            self.age = 0
            self.height = random.randint(5, 8)
            self.weight = random.randint(10, 16)
            self.strength = random.randint(10, 20)
            self.growspd = max(1, int((self.parents[0].growspd + self.parents[1].growspd) / 2 + random.randint(-2, 2)))
            self.hp = [max(20, int((self.parents[0].hp[1] + self.parents[1].hp[1]) /
                                   (25 * (self.parents[0].growspd + self.parents[1].growspd) / 2) + random.randint(-5, 5)))]
            self.hp.append(self.hp[0])
            self.skincolor = (random.randint(0, 255), random.randint(50, 200), random.randint(50, 200))
            self.nation = random.choice(self.parents).nation
            self.lang = 0
            if self.gender == 'male':
                self.occupation = self.parents[0].occupation
            else:
                self.occupation = self.parents[1].occupation
        else:
            self.age = 10
            self.height = random.randint(5, 8)
            self.weight = random.randint(10, 16)
            self.strength = random.randint(10, 20)
            self.growspd = random.randint(2, 7)
            self.hp = [random.randint(30, 50)]
            self.hp.append(self.hp[0])
            self.skincolor = (random.randint(0, 255), random.randint(50, 200), random.randint(50, 200))
            self.nation = 'unaffiliated'
            self.lang = 0
            self.occupation = occupation

    def update(self):
        pass


class World:
    def __init__(self):
        self.columns = 200
        self.rows = 150

        self.elevations = []
        self.biomes = []

        for y in range(0, self.rows):
            row = []
            row2 = []
            for x in range(0, self.columns):
                row.append(0)
                row2.append('none')
            self.biomes.append(row2)
            self.elevations.append(row)

        self.minlandratio = 0.5

        self.seed_of_seeds = [random.randint(int(self.columns / 4), int(3 * self.columns / 4)),
                              random.randint(int(2 * self.rows / 9), int(7 * self.rows / 9))]
        MAXDISTANCE = (self.columns + self.rows) / 2 / 10
        continentcount = random.randint(3, 8)
        barrier = random.randint(20, 50)
        self.master_seeds = []
        self.all_seeds = []
        self.all_spots = []
        self.all_isles = []

        print("*")

        for k in range(0, continentcount):
            while len(self.master_seeds) < 5 * int(2 / continentcount + 1) * k:
                x = int(max(0, self.seed_of_seeds[0] + MAXDISTANCE * random.randint(2, 13) / 10))
                y = int(max(0, self.seed_of_seeds[1] + MAXDISTANCE * random.randint(2, 12) / 10))
                sd = [min(x, self.columns - 1), min(y, self.rows - 1)]

                print(sd, [x, y])
                if sd not in self.master_seeds and 30 < sd[0] < self.columns - 30 and 30 < sd[1] < self.rows - 30:
                    self.master_seeds.append(sd)
                    self.all_seeds.append(sd)
                    self.all_spots.append(sd)
                if len(self.master_seeds) > 5:
                    break
            self.elevations[self.seed_of_seeds[1]][self.seed_of_seeds[0]] += 2
            rlc = [False, False]
            if self.seed_of_seeds[0] < self.columns / 2:
                pass

        print("~~", self.master_seeds)

        for ss in self.master_seeds:
            for _ in range(0, 5):
                sd = [int(min(max(ss[0] + MAXDISTANCE * random.randint(1, 9) / 30, 0), self.columns - 1)),
                      int(min(max(ss[1] + MAXDISTANCE * random.randint(1, 9) / 30, 0), self.rows - 1))]
                if (get_distance(sd, self.seed_of_seeds) < MAXDISTANCE and random.randint(0, 1000) < barrier) or\
                        random.randint(0, 1000) < 11 and sd != self.seed_of_seeds and 2 < sd[0] < self.columns - 2 and\
                        2 < sd[1] < self.rows - 2:
                    if random.randint(0, 17) < 1:
                        barrier = random.randint(30, 60)
                    self.all_seeds.append(sd)
                    if sd not in self.all_spots:
                        self.all_spots.append(sd)
                    self.elevations[sd[1]][sd[0]] += 0.4

        print("**", self.all_spots)
                    
        # Expand continents
        b = int((len(self.all_seeds) + MAXDISTANCE) * (self.columns * self.rows))
        for i in range(0, b):
            sd = random.choice(random.choice([self.all_seeds, self.all_spots, self.all_spots]))
            # print("~%s/%s - %s" % (i, b, sd))

            if 2 < sd[0] < self.columns - 3 and 2 < sd[1] < self.rows - 3:
                sd[0] += random.choice([-2, -1, -1, 0, 1, 1, -2])
                sd[1] += random.choice([-1, -1, -1, 0, 1, 1, 1])

                print("!%s/%s - %s" % (i, b, sd))
                i += 1
                if random.randint(0, 100) < 85:
                    self.elevations[sd[1] - 1][sd[0]] += random.randint(40, 80) / random.randint(90, 110)
                if random.randint(0, 100) < 85:
                    self.elevations[sd[1] + 1][sd[0]] += random.randint(40, 80) / random.randint(90, 110)
                if random.randint(0, 100) < 85:
                    self.elevations[sd[1]][sd[0] - 1] += random.randint(40, 80) / random.randint(90, 110)
                if random.randint(0, 100) < 85:
                    self.elevations[sd[1]][sd[0] + 1] += random.randint(40, 80) / random.randint(90, 110)
                if random.randint(0, 100) < 75:
                    self.elevations[sd[1] - 1][sd[0] - 1] += random.randint(20, 40) / random.randint(90, 110)
                    self.elevations[sd[1] - 1][sd[0] + 1] += random.randint(20, 40) / random.randint(90, 110)
                    self.elevations[sd[1] + 1][sd[0] - 1] += random.randint(20, 40) / random.randint(90, 110)
                    self.elevations[sd[1] + 1][sd[0] + 1] += random.randint(20, 40) / random.randint(90, 110)

                if sd in self.all_isles:
                    self.elevations[sd[1]][sd[0]] *= 1.1
                elif sd in self.all_seeds:
                    self.elevations[sd[1]][sd[0]] -= 0.3

                if random.randint(0, 100) < 85:
                    self.elevations[random.randint(0, self.rows - 1)][
                        random.randint(0, self.columns - 1)] *= random.randint(80, 100) / 100
                    self.elevations[random.randint(0, self.rows - 1)][
                        random.randint(0, self.columns - 1)] -= 0.1
                if sd not in self.all_spots and 1 < sd[0] < self.columns - 2 and 1 < sd[1] < self.rows - 2:
                    self.all_spots.append(sd)
            else:
                # print("*")
                pass

        abi = ""
        for y in range(0, self.rows):
            for x in range(0, self.columns):
                abi += "|%s" % int(self.elevations[y][x])
            abi += "|\n"
        # print(abi)

        for _ in range(0, 12 * int(MAXDISTANCE)):
            spot = [random.randint(2, self.columns - 2), random.randint(2, self.rows - 2)]
            if spot not in self.all_spots and spot not in self.all_isles:
                self.all_isles.append(spot)
                self.elevations[spot[1]][spot[0]] += random.choice([0.5, 1, 1])

        for _ in range(0, int(len(self.all_isles) / 2)):
            spot = random.choice(self.all_isles)
            self.elevations[spot[1]][spot[0]] += random.choice([0.5, 1])

        abi = ""
        for y in range(0, self.rows):
            for x in range(0, self.columns):
                abi += "|%s" % int(self.elevations[y][x])
            abi += "|\n"
        # print(abi)

        self.view()

    def view(self):
        self.scr = pygame.display.set_mode((self.columns * VIEWSCALE, self.rows * VIEWSCALE))
        pygame.init()
        pygame.display.set_caption("Mapview")
        viewing = True

        while viewing:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit()

            for y in range(0, self.rows):
                for x in range(0, self.columns):
                    tl = pygame.Surface((VIEWSCALE, VIEWSCALE))
                    vl = self.elevations[y][x]
                    color = (max(0, int(min(255, 255 * (vl / 11)))),
                                 max(0, int(min(255, 100 * (vl / 11)))),
                                 max(0, int(min(255, 255 * (vl / 11)))))
                    try:
                        tl.fill(color)
                    except:
                        print(color)
                    self.scr.blit(tl, (x * VIEWSCALE, y * VIEWSCALE))
            pygame.display.flip()


startup()

"""    def seed(self):
        print(self.elevations)
        if self.tilecount > 399:
            self.central_seed = [random.randint(int(self.columns / 25), self.columns - int(self.columns / 25)),
                                 random.randint(int(self.rows / 25), self.rows - int(self.rows / 25))]
        else:
            self.central_seed = [int(self.columns / 2), int(self.rows / 2)]
        self.elevations[self.central_seed[1]][self.central_seed[0]] = 9

        self.landseeds = [self.central_seed]
        self.allspots = [self.central_seed]
        self.seedlimit = int((self.rows + self.columns) / 2.8) + 8
        self.maxseeddistance = ((self.rows + self.columns) / 2.3) ** 1.1

        if self.tilecount < 150:
            self.minlandratio = 0.9
            self.maxseeddistance = (self.rows + self.columns) / 1.5
        elif self.tilecount < 750:
            self.minlandratio = 0.8
        elif self.tilecount < 1500:
            self.minlandratio = 0.6
        elif self.tilecount < 3000:
            self.minlandratio = 0.4
        else:
            self.minlandratio = 0.25

        while len(self.landseeds) < self.seedlimit:
            spot = [random.randint(0, self.columns - 1), random.randint(0, self.rows - 1)]
            print(spot, len(self.landseeds), self.seedlimit)
            if get_distance(spot, self.central_seed) < self.maxseeddistance:
                clusterable = False
                obsession = 0
                for s in self.landseeds:
                    obsession += 1
                    if get_distance(spot, s) < 4 or len(self.landseeds) < self.seedlimit / 3.2:
                        clusterable = True
                        break
                    if obsession > 500:
                        print('F')
                        break

                if clusterable:
                    if self.elevations[spot[1]][spot[0]] < 1:
                        self.elevations[spot[1]][spot[0]] = 1.2
                        self.landseeds.append(spot)
                        self.allspots.append(spot)
                    else:
                        self.elevations[spot[1]][spot[0]] += 0.7

                if obsession > 500:
                    print('F')
                    break
            else:
                self.elevations[random.randint(0, self.rows - 1)][random.randint(0, self.columns - 1)] += 0.1
                if spot not in self.allspots:
                    self.allspots.append(spot)

        for _ in range(0, int(max(1, self.tilecount / 1000))):
            spot = [random.randint(0, self.columns - 1), random.randint(0, self.rows - 1)]
            self.landseeds.append(spot)
            self.allspots.append(spot)

        abi = ''
        for row in self.elevations:
            for tile in row:
                if tile != 0:
                    abi += str(int(tile))
                else:
                    abi += '_'
            abi += '\n'

        print(abi)
        del abi

    def check_land(self, x, y):
        try:
            if self.elevations[y][x] > 1:
                return 0
            elif self.elevations[y][x] > 0:
                return 1
            else:
                return 2
        except IndexError:
            if x >= self.columns:
                xa = 0
            elif x < 0:
                xa = self.columns - 1
            else:
                xa = x

            if y >= self.rows:
                ya = self.rows - 1
            elif y < 0:
                ya = 0
            else:
                ya = y

            if self.elevations[ya][xa] > 1:
                return 0
            elif self.elevations[ya][xa] > 0:
                return 1
            else:
                return 2

    def checktile(self, board, x, y):
        try:
            return board[y][x]
        except IndexError:
            try:
                if x >= self.columns:
                    xa = 0
                elif x < 0:
                    xa = self.columns - 1
                else:
                    xa = x

                if y >= self.rows:
                    ya = self.rows - 1
                elif y < 0:
                    ya = 0
                else:
                    ya = y

                # print('yay', (x, y), board[ya][xa])
                return board[ya][xa]
            except IndexError:
                # print((x, y))
                return 1

    def checklandlocked(self, x, y):
        if self.check_land(x - 1, y - 1) == 0 and self.check_land(x, y - 1) == 0 and self.check_land(x + 1,
                                                                                                     y - 1) == 0 and \
                self.check_land(x - 1, y) == 0 and self.check_land(x, y) == 0 and self.check_land(x + 1, y) == 0 and \
                self.check_land(x - 1, y + 1) == 0 and self.check_land(x, y + 1) == 0 and self.check_land(x + 1,
                                                                                                          y + 1) == 0:
            return True
        else:
            return False

    def checkwaterlocked(self, x, y):
        if self.check_land(x - 1, y - 1) != 0 and self.check_land(x, y - 1) != 0 and self.check_land(x + 1,
                                                                                                     y - 1) != 0 and \
                self.check_land(x - 1, y) != 0 and self.check_land(x, y) != 0 and self.check_land(x + 1, y) != 0 and \
                self.check_land(x - 1, y + 1) != 0 and self.check_land(x, y + 1) != 0 and self.check_land(x + 1,
                                                                                                          y + 1) != 0:
            return True
        else:
            return False

    def checkcoastlocked(self, x, y):
        if self.check_land(x - 1, y - 1) > 0 and self.check_land(x, y - 1) > 0 and self.check_land(x + 1,
                                                                                                   y - 1) > 0 and \
                self.check_land(x - 1, y) > 0 and self.check_land(x, y) > 0 and self.check_land(x + 1, y) > 0 and \
                self.check_land(x - 1, y + 1) > 0 and self.check_land(x, y + 1) > 0 and self.check_land(x + 1,
                                                                                                        y + 1) > 0:
            return True
        else:
            return False

    def expand(self):
        print(int(((self.rows + self.columns) * 10.5) ** ((self.rows / 10) ** 0.6)))
        for _ in range(0, int(((self.rows + self.columns) * 10.5) ** ((self.rows / 10) ** 0.11))):
            anchor = random.choice(self.allspots)
            spot = random.choice([[anchor[0] + random.choice([-1, 0, 1]), anchor[1] + random.choice([-1, 1])],
                                  [anchor[0] + random.choice([-1, 1]), anchor[1] + random.choice([-1, 0, 1])]])

            if spot[0] < 0:
                spot[0] = self.columns - 1
            elif spot[0] > self.columns - 1:
                spot[0] = 0

            if spot[1] < 0 or spot[1] > self.rows - 1:
                spot[1] = anchor[1]
            self.allspots.append(spot)

            self.elevations[spot[1]][spot[0]] += 0.4
            if random.randint(0, 100) < 82:
                if random.randint(0, 100) < 78:
                    if 0 < spot[0]:
                        self.elevations[spot[1]][spot[0] - 1] += 0.06 / max(1, self.tilecount / 11000)
                    else:
                        self.elevations[spot[1]][self.columns - 1] += 0.06 / max(1, self.tilecount / 11000)

                if random.randint(0, 100) < 78:
                    if spot[0] < self.columns - 1:
                        self.elevations[spot[1]][spot[0] + 1] += 0.06 / max(1, self.tilecount / 11000)
                    else:
                        self.elevations[spot[1]][0] += 0.06 / max(1, self.tilecount / 11000)

                if 0 < spot[1] and random.randint(0, 100) < 78:
                    self.elevations[spot[1] - 1][spot[0]] += 0.06 / max(1, self.tilecount / 9500)
                if spot[1] < self.rows - 1 and random.randint(0, 100) < 78:
                    self.elevations[spot[1] + 1][spot[0]] += 0.06 / max(1, self.tilecount / 9000)

            self.elevations[random.randint(0, self.rows - 1)][random.randint(0, self.columns - 1)] -= 0.1

        islandcount = int((self.rows + self.columns) ** 0.8)
        islands = 0
        self.allislands = []
        while islands < islandcount:
            spot = [random.randint(0, self.columns - 1), random.randint(0, self.rows - 1)]
            if self.checkwaterlocked(spot[0], spot[1]):
                self.elevations[spot[1]][spot[0]] = random.choice([1.2, 2])
                islands += 1
                self.allspots.append(spot)
                self.allislands.append(spot)
                if random.randint(0, 100) < 59:
                    for _ in range(0, random.randint(0, 3)):
                        try:
                            self.elevations[spot[1] + random.choice([-1, 1])][spot[0] + random.choice([-1, 1])] += 1.2
                        except IndexError:
                            try:
                                if spot[0] == 0:
                                    xa = self.columns - 1
                                elif spot[0] == self.columns - 1:
                                    xa = 0
                                else:
                                    xa = spot[0] + random.choice([-1, 1])

                                if not 0 < spot[1] < self.columns - 1:
                                    ya = spot[1]
                                else:
                                    ya = spot[1] + random.choice([-1, 1])

                                self.elevations[ya][xa] += 1.2
                            except IndexError:
                                print('Error: ', spot)

        '''for y in range(0, self.rows):
            for x in range(0, self.columns):
                if self.elevations[y][x] < 0.6 and self.checkwaterlocked()'''

        self.columns *= 2
        small_elev = self.elevations
        self.elevations = []
        fullrows = []
        for y in range(0, self.rows):
            row = []
            for x in range(0, self.columns):
                if x % 2 == 0:
                    row.append(small_elev[y][int(x / 2)])
                else:
                    try:
                        row.append((small_elev[y][int((x - x % 2) / 2)] + small_elev[y][int((x - x % 2) / 2) + 1]) / 2)
                    except IndexError:
                        row.append((small_elev[y][int((x - x % 2) / 2)] + small_elev[y][0]))
            fullrows.append(row)

        self.rows *= 2
        for y in range(0, self.rows):
            if y % 2 == 0:
                self.elevations.append(fullrows[int((y - y % 2) / 2)])
            else:
                row = []
                for x in range(0, self.columns):
                    try:
                        vertavg = (fullrows[int((y - y % 2) / 2)][x] + fullrows[int((y - y % 2) / 2) + 1][x]) / 2
                    except IndexError:
                        vertavg = fullrows[int((y - y % 2) / 2)][x]

                    '''try:
                        horizavg = (fullrows[int((y - y % 2) / 2)][x] + fullrows[int((y - y % 2) / 2) + 1][x]) / 2
                    except IndexError:
                        horizavg = fullrows[int((y - y % 2) / 2)][x]'''

                    row.append(vertavg)
                self.elevations.append(row)

        for y in range(0, self.rows):
            for x in range(0, self.columns):
                if self.elevations[y][x] > 4:
                    self.elevations[y][x] **= 0.8 - (int(self.elevations[y][x] - 4) / max(22, (
                            (self.elevations[y][x] - 2) * 9) - random.randint(-3, 3))) * 1.1
        print(len(self.elevations[0]), len(self.elevations))

        abi = ''
        for n, row in enumerate(self.elevations):
            abi += '|'
            for n2, tile in enumerate(row):
                # print('(%s, %s)' % (n2, n))
                if tile > 1:
                    if random.randint(0, 100) < 13:
                        tile **= 0.15
                        abi += str(int(tile)) + '|'
                    else:
                        if tile > 1.5:
                            tile = math.sqrt(tile ** 1.1)
                            if tile > 8 and self.tilecount > 20000:
                                tile = tile ** 0.6
                        if int(tile) < 9:
                            abi += str(int(tile)) + '|'
                        else:
                            try:
                                if (self.elevations[n][n2 - 1] > 8.7 and self.elevations[n][n2 + 1] > 8.7) or \
                                        (self.elevations[n - 1][n2] > 8.7 and self.elevations[n + 1][n2] > 8.7):
                                    # tile = 0.4
                                    abi += '_|'
                                else:
                                    abi += '!|'
                            except IndexError:
                                tile = random.randint(7, 9)
                                abi += str(int(tile)) + '|'
                else:
                    abi += '_|'
            abi += '\n'

        print(abi)
        del islandcount, islands, small_elev, fullrows, abi
"""
