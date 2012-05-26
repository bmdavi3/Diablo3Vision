import math
from collections import deque

import cv

MOVING_AVG_LENGTH = 10


class Corners(object):
    def __init__(self):
        self.ul = deque([(0, 0)] * MOVING_AVG_LENGTH)
        self.ur = deque([(0, 0)] * MOVING_AVG_LENGTH)
        self.ll = deque([(0, 0)] * MOVING_AVG_LENGTH)
        self.lr = deque([(0, 0)] * MOVING_AVG_LENGTH)

    def add_corners(self, ul, ur, ll, lr):
        self.ul.append(ul)
        self.ul.popleft()

        self.ur.append(ur)
        self.ur.popleft()

        self.ll.append(ll)
        self.ll.popleft()

        self.lr.append(lr)
        self.lr.popleft()

    def average_points(self):
        average_points = []

        for points in (self.ul, self.ur,
                       self.ll, self.lr):

            x_total = 0
            y_total = 0

            for point in points:
                x_total += point[0]
                y_total += point[1]

            num_points = len(points)

            average_points.append((x_total / num_points,
                                   y_total / num_points))

        return average_points

    def get_corners(self, lines):
        ul = (10000, 10000)
        ur = (10000, 10000)
        ll = (10000, 10000)
        lr = (10000, 10000)

        for line in lines:
            for p in line:
                if distance(p, (0, 0)) < distance(ul, (0, 0)):
                    ul = p

                if distance(p, (640, 0)) < distance(ur, (640, 0)):
                    ur = p

                if distance(p, (0, 480)) < distance(ll, (0, 480)):
                    ll = p

                if distance(p, (640, 480)) < distance(lr, (640, 480)):
                    lr = p

        return (ul, ur, ll, lr)

    def scan(self, frame_gray):
        edges_image = cv.CreateImage(cv.GetSize(frame_gray),
                                     cv.IPL_DEPTH_8U, 1)
        cv.Canny(frame_gray, edges_image, 10, 120)

        lines = cv.HoughLines2(edges_image, cv.CreateMemStorage(),
                               cv.CV_HOUGH_PROBABILISTIC, 1, math.pi / 70,
                               10, 30, 20)

        new_corners = self.get_corners(lines)

        self.add_corners(new_corners[0], new_corners[1],
                         new_corners[2], new_corners[3])


def find_diablo_image(frame):
    small = cv.LoadImageM('pics/small2.png')

    result = cv.CreateImage(((frame.width - small.cols) + 1,
                             (frame.height - small.rows) + 1),
                            cv.IPL_DEPTH_32F, 1)

    cv.MatchTemplate(frame, small, result, cv.CV_TM_CCORR_NORMED)

    min_val, max_val, min_loc, max_loc = cv.MinMaxLoc(result)

    print max_val, max_loc


def closest(target, collection):
    return min((abs(target - i), i) for i in collection)[1]


def guess_ratio(p1, p2, p3, p4):
    distances = []

    distances.append(distance(p1, p2))
    distances.append(distance(p1, p3))
    distances.append(distance(p1, p4))
    distances.append(distance(p2, p3))
    distances.append(distance(p2, p4))
    distances.append(distance(p3, p4))

    distances.sort()

    ratios = [
        4.0 / 3,
        16.0 / 9,
        16.0 / 10
    ]

    ratio = (distances[3] + distances[2]) / (distances[1] + distances[0])

    return closest(ratio, ratios)


def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)


def repeat(capture, corners):
    frame = cv.QueryFrame(capture)

    frame_gray = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
    cv.CvtColor(frame, frame_gray, cv.CV_RGB2GRAY)

    corners.scan(frame_gray)

    ul, ur, ll, lr = corners.average_points()

    ratio = guess_ratio(ul, ur, ll, lr)

    cv.Circle(frame, ul, 10, cv.CV_RGB(255, 255, 255), 1)
    cv.Circle(frame, ur, 10, cv.CV_RGB(255, 255, 255), 1)
    cv.Circle(frame, ll, 10, cv.CV_RGB(255, 255, 255), 1)
    cv.Circle(frame, lr, 10, cv.CV_RGB(255, 255, 255), 1)

    new_height = frame.height
    new_width = int(frame.height * ratio)

    src = [ul, ll, ur, lr]
    dst = [(0, 0), (0, new_height),
           (new_width, 0), (new_width, new_height)]
    trans = cv.CreateMat(3, 3, cv.CV_32FC1)
    cv.GetPerspectiveTransform(src, dst, trans)

    pFrame = cv.CreateImage((new_width, new_height), cv.IPL_DEPTH_8U, 3)
    cv.WarpPerspective(frame, pFrame, trans)

    # find_diablo_image(pFrame)

    cv.ShowImage("w1", pFrame)
    cv.WaitKey(10)


def main():
    cv.NamedWindow("w1", cv.CV_WINDOW_AUTOSIZE)
    capture = cv.CaptureFromCAM(2)

    corners = Corners()

    while True:
        repeat(capture, corners)

if __name__ == "__main__":
    main()
