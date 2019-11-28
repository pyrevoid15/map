import pygame
import sys
import random
import math
import time
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
        random.seed(22222222222)

        self.seed()
        self.expand()

        self.hydrations = []
        self.temperatures = []
        self.fertilities = []
        self.biomes = []
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
            self.temperatures.append(row4)
            self.hydrations.append(row2)
            self.fertilities.append(row3)
            self.biomes.append(row5)

        self.ecolyze()
        if __name__ == '__main__':
            self.view()

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
                for x in range(1, int(self.columns - 1)):
                    self.elevations[y][x] = (self.elevations[y][x - 1] + self.elevations[y][x + 1] +
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
                                    if (self.elevations[n][n2 - 1] > 8.7 and self.elevations[n][n2 + 1] > 8.7) or \
                                            (self.elevations[n - 1][n2] > 8.7 and self.elevations[n + 1][n2] > 8.7):
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
                                self.hydrations[(y + j) % self.rows][(x + i) % self.columns] += 1 / (get_distance([x, y], [x + i, y + j]) ** (random.randint(20, 33) / random.randint(9, 17)))
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
                    self.hydrations[y][x] += 1 / (self.elevations[y][x] - 1) / 9

        for y in range(0, self.rows):
            for x in range(0, self.columns):
                distance = abs(self.rows / 2 - y) / self.rows
                if self.elevations[y][x] < 0:
                    albedo = 0.9
                elif self.elevations[y][x] < 1:
                    albedo = 1.2
                else:
                    albedo = (random.randint(14, 17) / 10) * 2 * self.elevations[y][x] * random.randint(990, 1110) / 1000

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
            if (0.3 < self.hydrations[b[1]][b[0]] < 1.9 and random.randint(0, 100) < 78) or random.randint(0, 100) < 45:
                t = 'forest'
            else:
                t = 'grass'

            strength = random.randint(30, 100) / 100
            for y in range(-int(self.maxseeddistance / random.randint(13, 17) * strength),
                           int(self.maxseeddistance / random.randint(13, 17) * strength)):
                for x in range(-int(self.maxseeddistance / random.randint(13, 17) * strength),
                               int(self.maxseeddistance / random.randint(13, 17) * strength)):
                    a = [b[0] + x, b[1] + y]
                    if (self.biomes[a[1] % self.rows][a[0] % self.columns] == 'none' and random.randint(0, 100) < 85) or\
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
                elif self.elevations[y][x] < 1.35 and self.hydrations[y][x] > 1.5:
                    self.biomes[y][x] = 'swamp'
                elif not self.checkcoastlocked(x, y) and self.elevations[y][x] < 1.2:
                    self.biomes[y][x] = 'beach'

                if self.elevations[y][x] > random.randint(42, 50) / 10 and self.biomes[y][x] == 'forest':
                    self.biomes[y][x] = 'grass'

                if self.biomes[y][x] == 'forest':
                    if self.temperatures[y][x] < random.randint(9, 23) / 10:
                        self.biomes[y][x] = 'taiga'
                    elif self.temperatures[y][x] > random.randint(40, 55) / 10 and self.hydrations[y][x] > 0.85:
                        self.biomes[y][x] = 'rainforest'
                elif self.biomes[y][x] == 'grass':
                    if self.temperatures[y][x] < random.randint(5, 16) / 10:
                        self.biomes[y][x] = 'tundra'
                    elif random.randint(37, 50) / 10 < self.temperatures[y][x] and self.hydrations[y][x] < 0.2:
                        self.biomes[y][x] = 'desert'

                if (self.biomes[y][x] == 'grass' or self.biomes[y][x] == 'desert' or self.biomes[y][x] == 'tundra') and\
                        self.elevations[y][x] > 5.5:
                    self.biomes[y][x] = 'mountain'

        for y in range(0, self.rows):
            print(y)
            row = []
            for x in range(0, self.columns):
                if self.elevations[y][x] < 0.5:
                    fert = 0
                elif self.elevations[y][x] < 1:
                    fert = 0.9
                elif self.elevations[y][x] > 4.5:
                    fert = -(4.5 / self.elevations[y][x]) * 2
                else:
                    if self.biomes[y][x] == 'swamp' or self.biomes[y][x] == 'beach':
                        fert = 0.2
                    elif self.biomes[y][x] == 'river':
                        fert = 0.7
                    elif self.biomes[y][x] == 'desert':
                        fert = 0.1
                    else:
                        fert = random.randint(60, 80) / random.randint(95, 120)

                if 0.5 < self.temperatures[y][x] < 5 and self.biomes[y][x] != 'desert':
                    fert *= (self.hydrations[y][x] / 3 + 1) * (self.temperatures[y][x] / 3 + 0.1) * random.randint(90, 110) / 100
                else:
                    fert *= (self.hydrations[y][x] / 3 + 1) * random.randint(90, 110) / 100
                row.append(fert)
            self.fertilities[y] = row

        for p in range(0, 2):
            for y in range(1, int(self.rows - 1)):
                for x in range(1, int(self.columns - 1)):
                    if 5.1 > self.elevations[y][x] > 0.55:
                        self.fertilities[y][x] = (self.fertilities[y][x - 1] + self.fertilities[y][x + 1] +
                                                  self.fertilities[y - 1][x] +
                                                  self.fertilities[y + 1][x]) / random.randint(36, 44) * 10

    def view(self):
        self.scr = pygame.display.set_mode((int(self.columns * VIEWSCALE), int(self.rows * VIEWSCALE)))
        pygame.init()
        pygame.display.set_caption("Mapview")
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
                elif e.type == pygame.KEYDOWN:
                    if 4 >= slider >= 0:
                        if e.key == pygame.K_LEFT and 0 < slider:
                            slider -= 1
                        elif e.key == pygame.K_RIGHT and slider < 4:
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
                        elif slider == 3:
                            for y in range(0, self.rows):
                                for x in range(0, self.columns):
                                    a = pygame.Surface((VIEWSCALE, VIEWSCALE))
                                    pygame.event.get()
                                    el = self.biomes[y][x]
                                    if el == 'ocean':
                                        color = (0, 0, 255)
                                    elif el == 'coast':
                                        color = (0, 70, 200)
                                    elif el == 'beach':
                                        color = (200, 200, 0)
                                    elif el == 'swamp':
                                        color = (10, 80, 60)
                                    elif el == 'grass':
                                        color = (30, 200, 40)
                                    elif el == 'mountain':
                                        color = (150, 150, 150)
                                    elif el == 'river':
                                        color = (0, 0, 255)
                                    elif el == 'forest':
                                        color = (10, 60, 10)
                                    elif el == 'tundra':
                                        color = (255, 255, 255)
                                    elif el == 'taiga':
                                        color = (170, 255, 200)
                                    elif el == 'desert':
                                        color = (150, 200, 30)
                                    elif el == 'rainforest':
                                        color = (10, 60, 0)
                                    else:
                                        color = [0, 0, 0]

                                    a.fill(color)
                                    self.scr.blit(a, (x * VIEWSCALE, y * VIEWSCALE))
                        elif slider == 4:
                            for y in range(0, self.rows):
                                for x in range(0, self.columns):
                                    a = pygame.Surface((VIEWSCALE, VIEWSCALE))
                                    pygame.event.get()
                                    el = self.fertilities[y][x]
                                    if el > 0:
                                        color = [0, min(255, (el + 3) / 6 * 255), 0]
                                    else:
                                        print([x, y])
                                        color = [0, 0, 0]

                                    a.fill(color)
                                    self.scr.blit(a, (x * VIEWSCALE, y * VIEWSCALE))

            if slider == 0:
                subject = self.elevations
            elif slider == 1:
                subject = self.hydrations
            elif slider == 2:
                subject = self.temperatures
            elif slider == 3:
                subject = self.biomes
            elif slider == 4:
                subject = self.fertilities
            elif slider == 5:
                subject = [[0, 0]]

            pygame.display.set_caption(str(((self.drivf[0] - self.drivf[0] % VIEWSCALE) / VIEWSCALE,
                                            (self.drivf[1] - self.drivf[1] % VIEWSCALE) / VIEWSCALE)) +
                                       str(subject[int((self.drivf[1] - self.drivf[1] % VIEWSCALE) / VIEWSCALE)]
                                           [int((self.drivf[0] - self.drivf[0] % VIEWSCALE) / VIEWSCALE)]))
            pygame.display.flip()
            time.sleep(0.1)


if __name__ == "__main__":
    g = Map()
