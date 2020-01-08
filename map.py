import pygame
import sys
import random
import math
import time
import io
import threading as thr

VIEWSCALE = 1


def get_distance(startpoint, endpoint):
    return math.sqrt((startpoint[0] - endpoint[0]) ** 2 + (startpoint[1] - endpoint[1]) ** 2)


# noinspection PyAttributeOutsideInit
class Map:
    def __init__(self):
        self.columns = 40
        self.rows = 40
        self.tilecount = self.columns * self.rows
        self.progress = 0

        self.elevations = []
        self.rivers = []
        self.peaks = []
        for _ in range(0, self.rows):
            row = []
            for _ in range(0, self.columns):
                row.append(0)
            self.elevations.append(row)

        print(random.getstate()[0])
        self.source = input("What is the seed:\t")

        if type(self.source) == str:
            if self.source.startswith("lo"):
                self.source = self.source.split(' ')
                self.source = ["load", self.source[1]]
            else:
                self.source = ["", self.source]
        else:
            self.source = ["", self.source]

        try:
            w = open(str(self.source[1]), 'r')
            w.close()

            self.source[1] = str(self.source[1])
        except FileNotFoundError:
            pass

        random.seed(self.source[1])

        self.hydrations = []
        self.temperatures = []
        self.fertilities = []
        self.biomes = []

        for _ in range(0, self.rows * 16):
            row = []
            row2 = []
            row3 = []
            row4 = []
            row5 = []
            for _ in range(0, self.columns * 16):
                row.append(0)
                row2.append(0)
                row3.append(0)
                row4.append(0)
                row5.append("none")
            self.temperatures.append(row4)
            self.hydrations.append(row2)
            self.fertilities.append(row3)
            self.biomes.append(row5)

        if self.source[0] != "load":
            self.seed()
            self.expand()
            self.ecolyze()
            self.namificationize()
        else:
            self.load()

        if __name__ == '__main__':
            self.view()

    def load(self):
        with open(self.source[1], "r+") as w:
            c = 0
            a: int = 0
            b: int = 0
            for line in w:
                if c == 0:
                    self.source:list = line.rstrip(']').lstrip('[').split(',')
                elif c == 1:
                    self.rows = int(line.rstrip())
                elif c == 2:
                    self.columns = int(line.rstrip())
                    print(self.columns, self.rows)
                    self.elevations = []
                    for _ in range(0, self.rows):
                        row = []
                        row2 = []
                        row3 = []
                        row4 = []
                        row5 = []
                        for _ in range(0, self.columns):
                            row.append(0)
                            row2.append(0)
                            row3.append(0)
                            row4.append(0)
                            row5.append("none")
                        self.elevations.append(row)
                        self.temperatures.append(row4)
                        self.hydrations.append(row2)
                        self.fertilities.append(row3)
                        self.biomes.append(row5)
                elif c == 3:
                    break
                c += 1

            abi = ""

            for line in w:
                for i in line:
                    if a == 0:
                        self.elevations[int(b / self.columns)][int(b % self.columns)] = ord(i) * 11 / 127
                    elif a == 1:
                        self.hydrations[int(b / self.columns)][int(b % self.columns)] = ord(i) * 4 / 127
                    elif a == 2:
                        self.temperatures[int(b / self.columns)][int(b % self.columns)] = ord(i) * 12 / 127
                    elif a == 3:
                        self.fertilities[int(b / self.columns)][int(b % self.columns)] = ord(i) * 9 / 127
                    elif a == 4:
                        el = ord(i) - 48
                        if el == 0:
                            el = 'ocean'
                        elif el == 1:
                            el = 'coast'
                        elif el == 2:
                            el = 'river'
                        elif el == 3:
                            el = 'swamp'
                        elif el == 4:
                            el = 'desert'
                        elif el == 5:
                            el = 'grass'
                        elif el == 6:
                            el = 'rainforest'
                        elif el == 7:
                            el = 'forest'
                        elif el == 8:
                            el = 'tundra'
                        elif el == 9:
                            el = 'taiga'
                        elif el == 10:
                            el = 'lake'
                        elif el == 11:
                            el = 'beach'
                        elif el == 12:
                            el = 'mountain'
                        elif el == 13:
                            el = 'peak'
                        elif el == 14:
                            el = 'summit'
                        self.biomes[int(b / self.columns)][int(b % self.columns)] = el

                    if a == 5:
                        a = 0
                        b += 1
                        continue
                    else:
                        a += 1


            w.close()
        print('Loaded map...')

    def seed(self):
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
            # print(spot, len(self.landseeds), self.seedlimit)
            if get_distance(spot, self.central_seed) < self.maxseeddistance:
                clusterable = False
                obsession = 0
                for s in self.landseeds:
                    obsession += 1
                    if get_distance(spot, s) < 4 or len(self.landseeds) < self.seedlimit / 3.2:
                        clusterable = True
                        break
                    if obsession > 500:
                        # print('F')
                        break

                if clusterable:
                    if self.elevations[spot[1]][spot[0]] < 1:
                        self.elevations[spot[1]][spot[0]] = 1.2
                        self.landseeds.append(spot)
                        self.allspots.append(spot)
                    else:
                        self.elevations[spot[1]][spot[0]] += 0.7

                if obsession > 500:
                    # print('F')
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
                    self.elevations[spot[1] % self.rows][(spot[0] - 1) % self.columns] += 0.06 / max(1,
                                                                                                     self.tilecount / 11000)
                    '''if 0 < spot[0]:
                        self.elevations[spot[1]][spot[0] - 1] += 0.06 / max(1, self.tilecount / 11000)
                    else:
                        self.elevations[spot[1]][self.columns - 1] += 0.06 / max(1, self.tilecount / 11000)'''

                if random.randint(0, 100) < 78:
                    self.elevations[spot[1] % self.rows][(spot[0] + 1) % self.columns] += 0.06 / max(1,
                                                                                                     self.tilecount / 11000)
                    '''if spot[0] < self.columns - 1:
                        self.elevations[spot[1]][spot[0] + 1] += 0.06 / max(1, self.tilecount / 11000)
                    else:
                        self.elevations[spot[1]][0] += 0.06 / max(1, self.tilecount / 11000)'''

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

        immunity = []
        for y in range(0, self.rows):
            for x in range(0, self.columns):
                try:
                    if self.elevations[y][x] > random.randint(35, 45) / 10 and \
                            self.elevations[y][x] > max(self.elevations[y - 1][x], self.elevations[y + 1][x],
                                                        self.elevations[x - 1][y], self.elevations[x + 1][y]):
                        self.peaks.append([x, y])
                        self.elevations[y][x] **= 1.4
                except IndexError:
                    pass

                if 1.6 < self.elevations[y][x] < 2.6:
                    self.elevations[y][x] **= 0.86

        for p in range(0, 4):
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
                        if p < random.choice([3, 4, 4, 2, 4, 4, 3, 4, 4]):
                            try:
                                row.append((small_elev[y][int((x - x % 2) / 2)] + small_elev[y][
                                    int((x - x % 2) / 2) + 1]) / 20 * random.randint(8, 12))
                            except IndexError:
                                row.append((small_elev[y][int((x - x % 2) / 2)] + small_elev[y][
                                    0] / 10 * random.randint(8, 12)))
                        else:
                            try:
                                row.append((small_elev[y][int((x - x % 2) / 2)] + small_elev[y][
                                    int((x - x % 2) / 2) + 1]) / 200 * random.randint(95, 105))
                            except IndexError:
                                row.append(
                                    (small_elev[y][int((x - x % 2) / 2)] +
                                     small_elev[y][0]) / 100 * random.randint(95, 105))
                fullrows.append(row)

            self.rows *= 2
            for y in range(0, self.rows):
                if y % 2 == 0:
                    self.elevations.append(fullrows[int((y - y % 2) / 2)])
                else:
                    row = []
                    for x in range(0, self.columns):
                        if p < random.choice([3, 4, 4, 2, 4, 4, 3, 4, 4]):
                            try:
                                vertavg = (fullrows[int((y - y % 2) / 2)][x] + fullrows[int((y - y % 2) / 2) + 1][
                                    x]) / 20 * random.randint(8, 12)
                            except IndexError:
                                vertavg = fullrows[int((y - y % 2) / 2)][x] / 10 * random.randint(8, 12)
                        else:
                            try:
                                vertavg = (fullrows[int((y - y % 2) / 2)][x] + fullrows[int((y - y % 2) / 2) + 1][
                                    x]) / 200 * random.randint(95, 105)
                            except IndexError:
                                vertavg = fullrows[int((y - y % 2) / 2)][x] / 100 * random.randint(95, 105)

                        row.append(vertavg)
                    self.elevations.append(row)

        for p in range(0, 2):
            for y in range(1, int(self.rows - 1)):
                for x in range(0, self.columns):
                    self.elevations[y][x] = (self.elevations[y][(x - 1) % self.columns] +
                                             self.elevations[y][(x + 1) % self.columns] +
                                             self.elevations[y - 1][x] +
                                             self.elevations[y + 1][x]) / random.randint(38, 42) * 10

        for y in range(0, self.rows):
            for x in range(0, self.columns):
                if self.elevations[y][x] > 1:
                    self.elevations[y][x] **= 0.8 - (int(self.elevations[y][x] - 4) / max(22, (
                            (self.elevations[y][x] - 2) * 9) - random.randint(-3, 3))) * 1.1
                elif self.elevations[y][x] < 1:
                    self.elevations[y][x] = (1 - self.elevations[y][x]) / 2
                    if self.elevations[y][x] < 0:
                        self.elevations[y][x] = 0

                if [x, y] in self.peaks:
                    self.elevations[y][x] **= 1.5
        print(len(self.elevations[0]), len(self.elevations))

        for n, row in enumerate(self.elevations):
            for n2, tile in enumerate(row):
                try:
                    if tile > 4:
                        tile **= 0.8 - (int(tile - 4) / max(22, (
                                (tile - 2) * 9) - random.randint(-3, 3))) * 1.1
                    if tile > 1:
                        if random.randint(0, 100) < 13:
                            tile **= 0.14
                        else:
                            if tile > 1.5:
                                tile = math.sqrt(tile ** 1.1)
                                if tile > 8 and self.tilecount > 20000:
                                    tile **= 0.6
                                if tile > 4:
                                    tile **= 1.1
                            else:
                                try:
                                    if (self.elevations[n][(n2 - 1) % self.columns] > 8.7 and
                                        self.elevations[n][(n2 + 1) % self.columns] > 8.7) or \
                                            (self.elevations[max(0, n - 1)][n2] > 8.7 and
                                             self.elevations[min(self.rows - 1, n + 1)][n2] > 8.7):
                                        pass
                                except IndexError:
                                    tile = random.randint(7, 9)
                except:
                    self.elevations[n][n2] = 0

                if type(tile) is not float:
                    self.elevations[n][n2] = 0

        for p in self.peaks:
            p[0] *= 16
            p[1] *= 16
            if p[0] < 0:
                p[0] += self.columns
            elif p[0] >= self.columns:
                p[0] -= self.columns
            if p[1] < 0:
                p[1] += self.rows
            elif p[1] >= self.rows:
                p[1] -= self.rows
            p[0] %= self.columns
            p[1] %= self.rows

            if self.elevations[p[1]][p[0]] is float:
                if self.elevations[p[1]][p[0]] > 0:
                    self.elevations[p[1]][p[0]] **= 1.3

        for y in range(0, self.rows):
            for x in range(0, self.columns):
                if self.elevations[y][x] < 1:
                    self.elevations[y][x] = 1 - self.elevations[y][x]

        abi = ''
        for n, row in enumerate(self.elevations):
            abi += '|'
            print(n)
            for n2, tile in enumerate(row):
                if tile > 1:
                    if int(tile) < 9:
                        abi += str(int(tile)) + '|'
                    else:
                        try:
                            if (self.elevations[n][n2 - 1] > 8.7 and self.elevations[n][n2 + 1] > 8.7) or \
                                    (self.elevations[n - 1][n2] > 8.7 and self.elevations[n + 1][n2] > 8.7):
                                abi += '_|'
                            else:
                                abi += '!|'
                        except IndexError:
                            abi += str(int(tile)) + '|'
                else:
                    abi += '_|'
            abi += '\n'

        print(abi)
        del islandcount, islands, abi

    def ecolyze(self):
        self.sources = []
        for _ in range(0, int(random.randint(4, 9) / 100 * self.tilecount)):
            loca = [0, 0]
            while True:
                loca = random.choice(self.peaks)
                loca[0] += random.randint(1, 6) * random.choice([-1, 1])
                loca[1] += random.randint(1, 6) * random.choice([-1, 1])

                if not ([loca[0] - 1, loca[1] - 1] in self.rivers or [loca[0] - 1, loca[1]] in self.rivers or
                        [loca[0] - 1, loca[1] + 1] in self.rivers or [loca[0], loca[1] - 1] in self.rivers or
                        [loca[0], loca[1] + 1] in self.rivers or [loca[0] + 1, loca[1] + 1] in self.rivers or
                        [loca[0] + 1, loca[1] - 1] in self.rivers or [loca[0] + 1, loca[1]] in self.rivers) and \
                        loca not in self.sources:
                    try:
                        if self.elevations[loca[1]][loca[0]] > 2 and \
                                0 < loca[0] < self.columns and 0 < loca[1] < self.rows:
                            self.rivers.append([loca[0], loca[1]])
                            self.sources.append([loca[0], loca[1]])

                            self.loca = loca
                            break
                    except:
                        try:
                            self.elevations[loca[1]][loca[0]] = 0
                        except:
                            pass

            flow = self.loca
            x = [0, 0]
            print("&", flow,
                  "---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---")
            prevflow = []
            amo = 0
            while amo < 250:
                try:
                    all_adj = [self.elevations[flow[1] - 1][flow[0] - 1], self.elevations[flow[1] - 1][flow[0]],
                               self.elevations[flow[1] - 1][flow[0] + 1],
                               self.elevations[flow[1]][flow[0] - 1], self.elevations[flow[1]][flow[0]],
                               self.elevations[flow[1]][flow[0] + 1],
                               self.elevations[flow[1] + 1][flow[0] - 1], self.elevations[flow[1] + 1][flow[0]],
                               self.elevations[flow[1] + 1][flow[0] + 1]]
                    for c, a in enumerate(all_adj):
                        p = [int(c % 3) - 1 + flow[0], int(c / 3) - 1 + flow[1]]
                        if a <= min(all_adj) + 0.15:
                            if a <= self.elevations[flow[1]][flow[0]] or random.randint(0, 100) < 93:
                                if p == flow or p in prevflow:
                                    all_adj[c] = 20
                                elif p in self.rivers:
                                    all_adj[c] = 20
                                    if p in self.sources:
                                        break
                                else:
                                    flow = p
                                    print("-")
                                    break
                            else:
                                self.elevations[int(c / 3) - 1 + flow[1] + random.choice([-1, 1])][
                                    int(c % 3) - 1 + flow[0] + random.choice([-1, 1])] -= 0.01
                                all_adj[c] = 20
                            self.elevations[p[1] + random.choice([-1, 1])][p[0] + random.choice([-1, 1])] -= 0.01
                        self.elevations[p[1] + random.choice([-1, 1])][p[0] + random.choice([-1, 1])] -= 0.001

                    if flow not in self.rivers:
                        print("<<<")
                        self.rivers.append(flow)
                        prevflow.append(flow)
                        amo += 1
                        if self.elevations[flow[1]][flow[0]] < 1:
                            prevflow.clear()
                            print("Low elevation")
                            break
                    elif flow in self.rivers:
                        print("Collided  ", flow)
                        prevflow.append(flow)
                        self.rivers.remove(flow)
                        self.rivers.append(flow)
                        amo += 1
                        if self.elevations[flow[1]][flow[0]] < 1 or flow in self.sources:
                            print("Low elevation")
                            prevflow.clear()
                            break
                        else:
                            flow[0] += random.randint(-1, 1)
                            flow[1] += random.randint(-1, 1)
                            if self.elevations[flow[1]][flow[0]] > self.elevations[prevflow[-1][1]][prevflow[-1][0]]:
                                flow = prevflow[-1]
                            else:
                                prevflow.append(flow)
                                self.rivers.append(flow)

                    if x == loca:
                        a = [flow[0] + random.randint(-1, 1), flow[1] + random.randint(-1, 1)]
                        amp = 0
                        while amp < 30:
                            flow = a
                            self.elevations[(flow[1] + random.choice([-1, 1])) % self.rows][
                                (flow[0] + random.choice([-1, 1])) % self.columns] -= 0.004
                            if self.elevations[a[1]][a[0]] < self.elevations[flow[1]][flow[0]] and \
                                    x == flow and a not in prevflow:
                                prevflow.append(flow)
                                if flow in self.sources:
                                    self.rivers.remove(flow)
                                    self.sources.remove(flow)
                                elif flow in self.rivers:
                                    self.rivers.remove(flow)
                                self.rivers.append(flow)
                                break
                            else:
                                a = [flow[0] + random.randint(-1, 1), flow[1] + random.randint(-1, 1)]
                                amp += 1
                                continue

                    x = flow

                    if self.elevations[flow[1]][flow[0]] < 1.2:
                        print("NEIN")
                        break
                except IndexError:
                    flow[0] %= self.columns
                    flow[1] %= self.rows
            print("$")
        print("$$$")
        print(sorted(self.rivers))

        self.rivers = sorted(self.rivers)

        donea = []
        for [x, y] in self.rivers:
            if [x, y] not in donea:
                donea.append([x, y])
                print("-+-", [x, y])
                self.hydrations[y][x] = 2
                for j in range(-50, 50):
                    for i in range(-50, 50):
                        if self.hydrations[(y + j) % self.rows][(x + i) % self.columns] < 1:
                            try:
                                self.hydrations[(y + j) % self.rows][(x + i) % self.columns] += 1 / (
                                        get_distance([x, y], [x + i, y + j]) ** (
                                        random.randint(23, 40) / random.randint(9, 17)))
                            except ZeroDivisionError:
                                pass

        del donea

        for y in range(0, self.rows):
            for x in range(0, self.columns):
                if self.elevations[y][x] < 1:
                    self.hydrations[y][x] = 2
                elif self.hydrations[y][x] > 2:
                    self.hydrations[y][x] = 2
                else:
                    try:
                        self.hydrations[y][x] += 1 / (self.elevations[y][x] - 1) / 9
                    except ZeroDivisionError:
                        self.hydrations[y][x] = 1.9

        for y in range(0, self.rows):
            for x in range(0, self.columns):
                distance = abs(self.rows / 2 - y) / self.rows
                if self.elevations[y][x] < 0:
                    albedo = 0.9
                elif self.elevations[y][x] < 1:
                    albedo = 1.2
                else:
                    albedo = (random.randint(14, 17) / 10) * 2 * self.elevations[y][x] * random.randint(990,
                                                                                                        1110) / 1000

                temp = (-12 * distance + 5 + 2 / albedo) * 1.23

                if temp > 10:
                    temp = 10
                self.temperatures[y][x] = temp + 1

        ye = 0
        for y in range(0, self.rows):
            for x in range(0, self.columns):
                if self.elevations[y][x] > 1:
                    ye += 1
        ye /= self.tilecount

        self.bioseeds = []
        print("+-+-")
        for _ in range(0, int(ye * self.rows / 1.6)):
            a = []
            while True:
                a = [random.randint(0, self.columns - 1), random.randint(0, self.rows - 1)]
                if self.elevations[a[1]][a[0]] > 1:
                    break
            self.bioseeds.append(a)

        for b in sorted(self.bioseeds):
            print(b)
            if (0.6 < self.hydrations[b[1]][b[0]] < 1.9 and random.randint(0, 100) < 75) or random.randint(0, 100) < 30:
                t = 'forest'
            else:
                t = 'grass'

            strength = random.randint(30, 100) / 100
            for y in range(-int(self.maxseeddistance / random.randint(13, 17) * strength),
                           int(self.maxseeddistance / random.randint(13, 17) * strength)):
                for x in range(-int(self.maxseeddistance / random.randint(13, 17) * strength),
                               int(self.maxseeddistance / random.randint(13, 17) * strength)):
                    a = [b[0] + x, b[1] + y]
                    if (self.biomes[a[1] % self.rows][a[0] % self.columns] == 'none' and random.randint(0, 100) < 85) or \
                            random.randint(0, 100) < 20:
                        self.biomes[a[1] % self.rows][a[0] % self.columns] = t

        for y in range(0, self.rows):
            for x in range(0, self.columns):
                if self.biomes[y][x] == 'none':
                    self.biomes[y][x] = 'grass'

        for y in range(0, self.rows):
            print(y)
            for x in range(0, self.columns):
                if self.elevations[y][x] < 0.5:
                    self.biomes[y][x] = 'ocean'
                elif self.elevations[y][x] < 1:
                    self.biomes[y][x] = 'coast'
                elif (self.hydrations[y][x] == 2 and self.elevations[y][x] > 1) or [x, y] in self.rivers:
                    self.biomes[y][x] = 'river'
                    if self.hydrations[y][x] > 2.1:
                        cc = 0
                        ac = 0
                        for c in range(0, 9):
                            f = [(x - 1 + c % 3) % self.columns, (y - 1 + int(c / 3)) % self.rows]
                            if self.biomes[f[1]][f[0]] == 'river':
                                cc += 1
                            elif self.biomes[f[1]][f[0]] == 'lake':
                                ac += 1
                            elif self.biomes[f[1]][f[0]] == 'coast':
                                cc = 0
                                ac = 0
                                break

                        if ((cc == 0 or 1) and (ac == 0 or 1)):
                            self.biomes[y][x] = 'lake'
                        elif ac > 2 and cc > 4 and ac + cc > 6:
                            self.biomes[y][x] = 'lake'
                        elif ac > 3 and cc > 0:
                            self.biomes[y][x] = 'lake'
                        elif self.hydrations[y][x] > 2.3 and self.biomes[y][x] == 'river' and cc + ac > 2:
                            self.biomes[y][x] = 'lake'

                        if self.hydrations[y][x] > 2.7:
                            self.biomes[y][x] = 'lake'
                elif self.elevations[y][x] < 1.36 and self.hydrations[y][x] > 1.67 and random.randint(0, 100) < 80:
                    self.biomes[y][x] = 'swamp'
                    if self.hydrations[y][x] >= 1.95:
                        self.biomes[y][x] = 'river'
                elif ((not self.checkcoastlocked(x, y) and (
                        not self.checklandlocked(x, y) or random.randint(0, 100) < 38)) and
                        self.elevations[y][x] < 1.2 and self.hydrations[y][x] < 1.5):
                    self.biomes[y][x] = 'beach'

                if self.elevations[y][x] > random.randint(42, 50) / 10 and self.biomes[y][x] == 'forest':
                    self.biomes[y][x] = 'grass'

                if self.biomes[y][x] == 'forest':
                    if self.temperatures[y][x] > 40 and self.hydrations[y][x] < 0.3 and random.randint(0, 100) < 98:
                        self.biomes[y][x] = 'desert'
                    elif self.temperatures[y][x] < random.randint(12, 26) / 10:
                        self.biomes[y][x] = 'taiga'
                    elif self.temperatures[y][x] > (random.randint(40, 55) + 0.75) / 10 and self.hydrations[y][x] > 0.85:
                        self.biomes[y][x] = 'rainforest'
                elif self.biomes[y][x] == 'grass':
                    if self.temperatures[y][x] < random.randint(8, 21) / 10:
                        self.biomes[y][x] = 'tundra'
                    elif random.randint(37, 50) / 10 < self.temperatures[y][x] and self.hydrations[y][x] < 0.275:
                        self.biomes[y][x] = 'desert'

                if (self.biomes[y][x] == 'grass' or self.biomes[y][x] == 'desert' or self.biomes[y][x] == 'tundra') and \
                        self.elevations[y][x] > 5.5:
                    self.biomes[y][x] = 'mountain'
                    if self.elevations[y][x] > 6.5:
                        self.biomes[y][x] = 'summit'
                        if self.elevations[y][x] > 7.5:
                            self.biomes[y][x] = 'peak'

        for y in range(0, self.rows):
            print(y)
            row = []
            for x in range(0, self.columns):
                if self.biomes[y][x] == 'river':
                    if self.hydrations[y][x] > 2.1:
                        cc = 0
                        ac = 0
                        for c in range(0, 9):
                            f = [(x - 1 + c % 3) % self.columns, (y - 1 + int(c / 3)) % self.rows]
                            if self.biomes[f[1]][f[0]] == 'river':
                                cc += 1
                            elif self.biomes[f[1]][f[0]] == 'lake':
                                ac += 1
                            elif self.biomes[f[1]][f[0]] == 'coast':
                                cc = 0
                                ac = 0
                                break

                        if ((cc == 0 or 1) and (ac == 0 or 1)):
                            self.biomes[y][x] = 'lake'
                        elif ac > 2 and cc > 4 and ac + cc > 6:
                            self.biomes[y][x] = 'lake'
                        elif ac > 3 and cc > 0 and ac + cc > 4:
                            self.biomes[y][x] = 'lake'
                        elif ac + cc > 6:
                            self.biomes[y][x] = 'lake'
                        elif self.hydrations[y][x] > 2.3 and self.biomes[y][x] == 'river' and cc + ac > 2:
                            self.biomes[y][x] = 'lake'
                        elif self.hydrations[y][x] > 3:
                            self.biomes[y][x] = 'lake'
                elif self.biomes[y][x] == 'desert':
                    cc = 0
                    for c in range(0, 9):
                        f = [(x - 1 + c % 3) % self.columns, (y - 1 + int(c / 3)) % self.rows]
                        if self.biomes[f[1]][f[0]] == 'desert':
                            cc += 1

                    if 9 > cc > 6:
                        ac = 0
                        for c in range(0, 9):
                            f = [(x - 1 + c % 3) % self.columns, (y - 1 + int(c / 3)) % self.rows]
                            if self.biomes[f[1]][f[0]] == 'forest' and random.randint(0, 100) < 96:
                                self.biomes[f[1]][f[0]] = random.choice(
                                    ['grass', 'grass', 'desert', 'desert', 'desert', 'desert', 'desert'])
                            elif self.biomes[f[1]][f[0]] == 'grass' and random.randint(0, 100) < 74:
                                self.biomes[f[1]][f[0]] = 'desert'

                if self.biomes[y][x] == 'ocean':
                    fertbio = 0
                elif self.biomes[y][x] == 'coast':
                    fertbio = 0.2
                elif self.biomes[y][x] == 'trench':
                    fertbio = 0
                elif self.biomes[y][x] == 'grass':
                    fertbio = 2.1
                elif self.biomes[y][x] == 'tundra':
                    fertbio = 1.2
                elif self.biomes[y][x] == 'taiga':
                    fertbio = 0.9
                elif self.biomes[y][x] == 'forest':
                    fertbio = 1.7
                elif self.biomes[y][x] == 'reef':
                    fertbio = 0.4
                elif self.biomes[y][x] == 'rainforest':
                    fertbio = 1.5
                elif self.biomes[y][x] == 'desert':
                    fertbio = 0.2
                elif self.biomes[y][x] == 'swamp':
                    fertbio = 0.22
                elif self.biomes[y][x] == 'beach':
                    fertbio = 0.1
                elif self.biomes[y][x] == 'mountain' or self.biomes[y][x] == 'summit':
                    fertbio = max(0, 1.1 - (self.elevations[y][x] - 5) / 100)
                else:
                    fertbio = 1.6

                fertbio *= random.randint(5, 11) / 10

                fertbio = max(0, int((fertbio * (
                        1.25 + random.randint(0, 12) / 20 - max(0, (self.elevations[y][x] + 1) / 3.5) / 2)) ** 2))
                if self.biomes != 'coast' and self.biomes != 'ocean':
                    fertbio += max(0.1, self.hydrations[y][x]) ** 2 / 6
                if fertbio < 0.01:
                    fertbio = 0

                row.append(max(0, fertbio))
            self.fertilities[y] = row

        for p in range(0, 2):
            for y in range(1, int(self.rows - 1)):
                for x in range(1, int(self.columns - 1)):
                    if 5.1 > self.elevations[y][x] > 0.55:
                        self.fertilities[y][x] = (self.fertilities[y][x - 1] + self.fertilities[y][x + 1] +
                                                  self.fertilities[y - 1][x] +
                                                  self.fertilities[y + 1][x]) / random.randint(36, 44) * 10

    def gen_name(self):
        consonants = ['b', 'c', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'p', 'q', 'r', 's', 's', 't',
                      't', 'v', 'w', 'x', 'y', 'z', 'z']
        vowels = ['a', 'e', 'i', 'o', 'u', 'y']

        syllables = []
        word = ""
        for _ in range(0, random.randint(1, 5)):
            syl = ""
            if word == "":
                if random.randint(0, 100) < 35:
                    syl += random.choice(vowels)

                    if syl[0] == 'a' and random.randint(0, 100) < 32:
                        syl += random.choice(['e', 'u'])
                    elif syl[0] == 'e' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i', 'u'])
                    elif syl[0] == 'o' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i', 'u', 'y'])
                    elif syl[0] == 'u' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i'])
                    elif syl[0] != 'y':
                        syl += syl[0]

                else:
                    syl += random.choice(consonants)

                    if (syl[0] == 'c' or 'p' or 's' or 'z' or 't' or 'g' or 'k') and random.randint(0, 100) < 40:
                        syl += 'h'
                    elif syl[0] == 'q':
                        syl += 'u'

                    syl += random.choice(vowels)

                    if syl[-1] == 'a' and random.randint(0, 100) < 32:
                        syl += random.choice(['e', 'u'])
                    elif syl[-1] == 'e' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i', 'u'])
                    elif syl[-1] == 'o' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i', 'u', 'y'])
                    elif syl[-1] == 'u' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i'])
                    elif syl[-1] != 'y':
                        syl += syl[-1]
            else:
                if syllables[-1][-1] in consonants:
                    syl += random.choice(vowels)

                    if syl[0] == 'a' and random.randint(0, 100) < 32:
                        syl += random.choice(['e', 'u'])
                    elif syl[0] == 'e' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i', 'u'])
                    elif syl[0] == 'o' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i', 'u', 'y'])
                    elif syl[0] == 'u' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i'])
                    elif syl[0] != 'y':
                        syl += syl[0]

                else:
                    syl += random.choice(consonants)

                    if (syl[0] == 'c' or 'p' or 's' or 'z' or 't' or 'g' or 'k') and random.randint(0, 100) < 40:
                        syl += 'h'
                    elif syl[0] == 'q':
                        syl += 'u'
                    elif syl[0] == 'n' and random.randint(0, 100) < 11:
                        syl += 'g'
                    elif (syl[0] == 'l' or 'g' or 't' or 'c' or 's' or 'd' or 'f' or 'z' or 'b' or 'n' or 'm') and \
                            random.randint(0, 100) < 15:
                        syl += syl[-1]

                    syl += random.choice(vowels)

                    if syl[-1] == 'a' and random.randint(0, 100) < 32:
                        syl += random.choice(['e', 'u'])
                    elif syl[-1] == 'e' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i', 'u'])
                    elif syl[-1] == 'o' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i', 'u', 'y'])
                    elif syl[-1] == 'u' and random.randint(0, 100) < 20:
                        syl += random.choice(['a', 'i'])
                    elif syl[-1] != 'y':
                        syl += syl[-1]
            syllables.append(syl)

        for s in syllables:
            word += s

        return word

    def namificationize(self):
        self.all_names = ['Unknown']
        self.all_sizes = [640 ** 2]
        self.toponymy = []
        self.biosizes = []

        for y in range(0, self.rows):
            row = []
            for x in range(0, self.columns):
                row.append(0)
            self.toponymy.append(row)
            self.biosizes.append(row)

        placecounter = 0
        """for y in range(0, self.rows):
            for x in range(0, self.columns):
                print(placecounter)
                if self.toponymy[y][x] == 0:
                    placetype = self.biomes[y][x]
                    cc = 0
                    for c in range(0, 9):
                        f = [(x - 1 + c % 3) % self.columns, (y - 1 + int(c / 3)) % self.rows]
                        alpha = self.biomes[f[1]][f[0]]
                        if alpha == placetype:
                            cc += 1

                    if cc > 1 or random.randint(0, 30) < 1:
                        placecounter += 1
                        self.toponymy[y][x] = placecounter
                        size = 0
                        allinplace = [[x, y]]

                        if placetype == 'ocean':
                            multiplier = 450
                        elif placetype == 'coast':
                            multiplier = 30
                        elif placetype == 'forest' or 'rainforest' or 'taiga':
                            multiplier = 12
                        elif placetype == 'grass' or 'tundra':
                            multiplier = 12
                        elif placetype == 'desert':
                            multiplier = 25
                        elif placetype == 'mountain':
                            multiplier = 3
                        elif placetype == 'peak' or 'summit':
                            multiplier = 2
                        else:
                            multiplier = 1

                        obsession = 0
                        nextt = [x, y]
                        availablenext = []
                        self.all_names.append((self.gen_name() + placetype).title())

                        while size < 3600 * multiplier and obsession < 175 * multiplier:
                            print(">", placecounter)
                            if random.randint(0, 100) < 0:
                                expando = True
                            else:
                                expando = False
                            if placetype == 'forest' or 'rainforest' or 'taiga' or 'grass' or 'tundra':
                                for c in range(0, 25):
                                    f = [(nextt[0] - 2 + c % 5) % self.columns, (nextt[1] - 2 + int(c / 5)) % self.rows]
                                    if self.biomes[f[1]][f[0]] == placetype and f not in allinplace and (self.toponymy[f[1]][f[0]] == 0 or expando):
                                        allinplace.append(f)
                                        availablenext.append(f)
                                        self.toponymy[f[1]][f[0]] = placecounter
                                        size += 1
                                        obsession -= random.choice([2, 2, 2, 4, 4, 5, 5, 5, 6, 9]) / 1.3
                                    else:
                                        obsession += 1
                            else:
                                for c in range(0, 9):
                                    f = [(nextt[0] - 1 + c % 3) % self.columns, (nextt[1] - 1 + int(c / 3)) % self.rows]
                                    if self.biomes[f[1]][f[0]] == placetype and f not in allinplace and (self.toponymy[f[1]][f[0]] == 0 or expando):
                                        allinplace.append(f)
                                        availablenext.append(f)
                                        self.toponymy[f[1]][f[0]] = placecounter
                                        size += 1
                                        obsession -= random.choice([2, 2, 2, 4, 4, 5, 5, 5, 6, 9])
                                    else:
                                        obsession += 1
                            try:
                                nextt = random.choice(availablenext)
                                availablenext.remove(nextt)
                            except IndexError:
                                pass

                            for c in allinplace:
                                self.biosizes[c[1]][c[0]] = size
                    else:
                        self.toponymy[y][x] = random.choice([self.toponymy[(x + self.columns - 1) % self.columns][y], self.toponymy[max(0, y - 1)][x]])"""

    def view(self):
        self.scr = pygame.display.set_mode((int(self.columns * VIEWSCALE), int(self.rows * VIEWSCALE)))
        pygame.init()
        pygame.display.set_caption("Mapview: " + str(self.source))
        pygame.display.set_icon(pygame.image.load('icon.png'))

        viewing = True
        self.scr.fill((255, 255, 255))
        slider = 0
        self.drivf = []

        for y in range(0, int(len(self.elevations))):
            print(y)
            for x in range(0, int(len(self.elevations[0]))):
                a = pygame.Surface((VIEWSCALE, VIEWSCALE))
                self.drivf = pygame.mouse.get_pos()

                pygame.event.get()
                el = self.elevations[y][x]
                if el > 1:
                    color = [max(0, min(255, int(el / 11 * 255))), 0, 0]
                else:
                    color = [0, 0, 255]

                a.fill(color)
                self.scr.blit(a, (x * VIEWSCALE, y * VIEWSCALE))
                # pygame.display.flip()

        while viewing:
            self.drivf = pygame.mouse.get_pos()
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit()
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_s:
                        with open(str(self.source[1]), "w+") as w:
                            w.write(self.source[1] + "\n" + str(self.columns) + "\n" + str(self.rows) + "\n\n")
                            for y in range(0, self.rows):
                                for x in range(0, self.columns):
                                    if self.hydrations[y][x] < 0:
                                        self.hydrations[y][x] = 0
                                    elif self.hydrations[y][x] > 126:
                                        self.hydrations[y][x] = 126

                                    # ------------------------------------------------------------------------- #
                                    print(chr(int(min(126, max(0, self.elevations[y][x] * 128 / 11)))), '\n',
                                          chr(int(min(126, max(0, self.hydrations[y][x] * 128 / 4)))), '\n',
                                          chr(int(min(126, max(0, self.temperatures[y][x] * 128 / 12)))), '\n',
                                          chr(int(min(126, max(0, self.fertilities[y][x] * 128 / 9)))))
                                    # ------------------------------------------------------------------------- #

                                    w.write(chr(int(min(126, max(0, self.elevations[y][x] * 128 / 11)))))
                                    w.write(chr(int(min(126, max(0, self.hydrations[y][x] * 128 / 4)))))
                                    w.write(chr(int(min(126, max(0, self.temperatures[y][x] * 128 / 12)))))
                                    w.write(chr(int(min(126, max(0, self.fertilities[y][x] * 128 / 9)))))
                                    el = self.biomes[y][x][0:2]

                                    if el == 'oc':
                                        el = 0
                                    elif el == 'co':
                                        el = 1
                                    elif el == 'ri':
                                        el = 2
                                    elif el == 'sw':
                                        el = 3
                                    elif el == 'de':
                                        el = 4
                                    elif el == 'gr':
                                        el = 5
                                    elif el == 'ra':
                                        el = 6
                                    elif el == 'fo':
                                        el = 7
                                    elif el == 'tu':
                                        el = 8
                                    elif el == 'ta':
                                        el = 9
                                    elif el == 'la':
                                        el = 10
                                    elif el == 'be':
                                        el = 11
                                    elif el == 'mo':
                                        el = 12
                                    elif el == 'pe':
                                        el = 13
                                    elif el == 'su':
                                        el = 14
                                    w.write(chr(el + 48))
                                    w.write('¡')
                                # w.write('¢')
                            w.close()
                        print('Saved map...\t', self.source[1])

                    if 5 >= slider >= 0:
                        if e.key == pygame.K_LEFT and 0 < slider:
                            slider -= 1
                        elif e.key == pygame.K_RIGHT and slider < 5:
                            slider += 1

                        if slider == 0:
                            for y in range(0, int(len(self.elevations))):
                                for x in range(0, int(len(self.elevations[0]))):
                                    a = pygame.Surface((VIEWSCALE, VIEWSCALE))
                                    self.drivf = pygame.mouse.get_pos()
                                    pygame.event.get()
                                    el = self.elevations[y][x]
                                    if el > 1:
                                        color = [max(0, min(255, int(el / 11 * 255))), 0, 0]
                                    else:
                                        color = [0, 0, 255]

                                    a.fill(color)
                                    self.scr.blit(a, (x * VIEWSCALE, y * VIEWSCALE))
                        elif slider == 1:
                            for y in range(0, self.rows):
                                for x in range(0, self.columns):
                                    a = pygame.Surface((VIEWSCALE, VIEWSCALE))
                                    pygame.event.get()
                                    el = self.hydrations[y][x]
                                    if 0 < el < 1:
                                        color = [0, 0, max(0, min(255, int(el / 1 * 255)))]
                                    elif el > 1:
                                        color = [0, 0, max(0, min(255, int((el - 1) / 1 * 255)))]
                                    else:
                                        color = [0, 0, 0]

                                    a.fill(color)
                                    self.scr.blit(a, (x * VIEWSCALE, y * VIEWSCALE))
                        elif slider == 2:
                            for y in range(0, self.rows):
                                for x in range(0, self.columns):
                                    a = pygame.Surface((VIEWSCALE, VIEWSCALE))
                                    pygame.event.get()
                                    el = self.temperatures[y][x]
                                    if el != 0:
                                        multiplier = 255 / 3
                                        color = ((min(255, max(multiplier * (-(el - 9) ** 2 / 3 + 3), 0)),
                                                  min(255, max(multiplier * (-(el - 6) ** 2 / 3 + 3), 0)),
                                                  min(255, max(multiplier * (-(el - 3) ** 2 / 3 + 3), 0))))
                                    else:
                                        color = [0, 0, 0]

                                    a.fill(color)
                                    self.scr.blit(a, (x * VIEWSCALE, y * VIEWSCALE))
                        elif slider == 4:
                            for y in range(0, self.rows):
                                for x in range(0, self.columns):
                                    a = pygame.Surface((VIEWSCALE, VIEWSCALE))
                                    pygame.event.get()
                                    el = self.biomes[y][x]
                                    if el == 'ocean' or el == 'river':
                                        color = (0, 0, 255)
                                    elif el == 'coast' or el == 'lake':
                                        color = (0, 70, 200)
                                    elif el == 'beach':
                                        color = (200, 200, 0)
                                    elif el == 'swamp':
                                        color = (10, 80, 60)
                                    elif el == 'grass':
                                        color = (30, 200, 40)
                                    elif el == 'mountain':
                                        color = (150, 150, 150)
                                    elif el == 'summit':
                                        color = (202, 202, 202)
                                    elif el == 'forest':
                                        color = (22, 100, 10)
                                    elif el == 'tundra' or el == 'peak':
                                        color = (255, 255, 255)
                                    elif el == 'taiga':
                                        color = (170, 255, 200)
                                    elif el == 'desert':
                                        color = (150, 200, 30)
                                    elif el == 'rainforest':
                                        color = (10, 40, 0)
                                    else:
                                        color = [0, 0, 0]

                                    a.fill(color)
                                    self.scr.blit(a, (x * VIEWSCALE, y * VIEWSCALE))
                        elif slider == 3:
                            for y in range(0, self.rows):
                                for x in range(0, self.columns):
                                    a = pygame.Surface((VIEWSCALE, VIEWSCALE))
                                    pygame.event.get()
                                    el = self.fertilities[y][x]

                                    if el > 9:
                                        self.fertilities[y][x] = 9
                                        el = 9

                                    if el >= 0:
                                        value = 255 - min(255, max(0, el) / 9 * 255)
                                        color = (value, 255, value)
                                    else:
                                        value = 255 - min(255, max(0, -el) / 5 * 255)
                                        color = (value, value, value)

                                    a.fill(color)
                                    self.scr.blit(a, (x * VIEWSCALE, y * VIEWSCALE))
                        elif slider == 5:
                            highlightcolors = [(100, 100, 100), (255, 255, 255), (255, 0, 0), (255, 255, 0),
                                               (0, 255, 0), (0, 255, 255), (0, 0, 255), (100, 0, 0), (100, 100, 0),
                                               (0, 100, 0), (0, 100, 100), (0, 0, 100), (50, 0, 0), (50, 50, 0),
                                               (0, 50, 0), (0, 50, 50), (0, 0, 50), (200, 0, 0), (200, 200, 0),
                                               (0, 200, 0), (0, 200, 200), (0, 0, 200)]
                            for y in range(0, self.rows):
                                for x in range(0, self.columns):
                                    a = pygame.Surface((VIEWSCALE, VIEWSCALE))
                                    pygame.event.get()
                                    el = self.toponymy[y][x]
                                    if el == 0:
                                        color = (0, 0, 0)
                                    else:
                                        color = highlightcolors[el % len(highlightcolors)]

                                    a.fill(color)
                                    self.scr.blit(a, (x * VIEWSCALE, y * VIEWSCALE))

            if slider == 0:
                subject = self.elevations
            elif slider == 1:
                subject = self.hydrations
            elif slider == 2:
                subject = self.temperatures
            elif slider == 4:
                subject = self.biomes
            elif slider == 3:
                subject = self.fertilities
            elif slider == 5:
                subject = self.toponymy

            if slider != 5:
                pygame.display.set_caption(str(((self.drivf[0] - self.drivf[0] % VIEWSCALE) / VIEWSCALE,
                                                (self.drivf[1] - self.drivf[1] % VIEWSCALE) / VIEWSCALE)) +
                                           str(subject[int((self.drivf[1] - self.drivf[1] % VIEWSCALE) / VIEWSCALE)]
                                               [int((self.drivf[0] - self.drivf[0] % VIEWSCALE) / VIEWSCALE)]))
            else:
                try:
                    pygame.display.set_caption(str(((self.drivf[0] - self.drivf[0] % VIEWSCALE) / VIEWSCALE,
                                                    (self.drivf[1] - self.drivf[1] % VIEWSCALE) / VIEWSCALE)) +
                                               self.all_names[subject[
                                                   int((self.drivf[1] - self.drivf[1] % VIEWSCALE) / VIEWSCALE)][
                                                   int((self.drivf[0] - self.drivf[0] % VIEWSCALE) / VIEWSCALE)]] +
                                               str(self.biosizes[
                                                       int((self.drivf[1] - self.drivf[1] % VIEWSCALE) / VIEWSCALE)][
                                                       int((self.drivf[0] - self.drivf[0] % VIEWSCALE) / VIEWSCALE)]))
                except:
                    pygame.display.set_caption(str(((self.drivf[0] - self.drivf[0] % VIEWSCALE) / VIEWSCALE,
                                                    (self.drivf[1] - self.drivf[1] % VIEWSCALE) / VIEWSCALE)) +
                                               self.all_names[subject[
                                                   int((self.drivf[1] - self.drivf[1] % VIEWSCALE) / VIEWSCALE)][
                                                   int((self.drivf[0] - self.drivf[0] % VIEWSCALE) / VIEWSCALE)]])

            pygame.display.flip()
            time.sleep(0.1)


if __name__ == "__main__":
    g = Map()
