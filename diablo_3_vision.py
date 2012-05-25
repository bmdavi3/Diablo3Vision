import math

import cv

def template_match():
    small = cv.LoadImageM('pics/small.png')
    large = cv.LoadImageM('pics/large1.png')

    # result = cv.CreateMat((large.cols - small.cols) + 1, (large.rows - small.rows) + 1, cv.CV_32F)
    result = cv.CreateImage(((large.cols - small.cols) + 1, (large.rows - small.rows) + 1), cv.IPL_DEPTH_32F, 1)

    cv.MatchTemplate(large, small, result, cv.CV_TM_CCORR_NORMED)

    min_val, max_val, min_loc, max_loc = cv.MinMaxLoc(result)

    print max_loc


cv.NamedWindow("w1", cv.CV_WINDOW_AUTOSIZE)
capture = cv.CaptureFromCAM(0)

def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

def get_corners(lines):
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

def repeat():
    frame = cv.QueryFrame(capture)

    # frame2 = cv.CreateImage((frame.height, frame.width), cv.CV_32FC1, 1)
    # cv.ConvertScale(frame, frame2)
    frame_gray = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
    cv.CvtColor(frame, frame_gray, cv.CV_RGB2GRAY)

    edges_image = cv.CreateImage(cv.GetSize(frame), cv.IPL_DEPTH_8U, 1)
    cv.Canny(frame_gray, edges_image, 10, 120)

    lines = cv.HoughLines2(edges_image, cv.CreateMemStorage(),
                           cv.CV_HOUGH_PROBABILISTIC, 1, math.pi / 70,
                           10, 20, 20)

    # for line in lines:
    #     cv.Line(frame, line[0], line[1], (0, 0, 255), 3)

    ul, ur, ll, lr = get_corners(lines)

    cv.Circle(frame, ul, 10, cv.CV_RGB(255, 255, 255), 1)
    cv.Circle(frame, ur, 10, cv.CV_RGB(255, 255, 255), 1)
    cv.Circle(frame, ll, 10, cv.CV_RGB(255, 255, 255), 1)
    cv.Circle(frame, lr, 10, cv.CV_RGB(255, 255, 255), 1)

    print ul, ur, ll, lr
    cv.Circle(frame, (10, 10), 10, cv.CV_RGB(255, 0, 0), 1)

    src = [ul, ll, ur, lr]
    dst = [(0, 0), (0, frame.height),
           (frame.width, 0), (frame.width, frame.height)]
    trans = cv.CreateMat(3, 3, cv.CV_32FC1)
    cv.GetPerspectiveTransform(src, dst, trans)

    pFrame = cv.CreateImage((frame.width, frame.height), cv.IPL_DEPTH_8U, 3)
    cv.WarpPerspective(frame, pFrame, trans)


    # eig_image = cv.CreateMat(frame.height, frame.width, cv.CV_32FC1)
    # temp_image = cv.CreateMat(frame.height, frame.width, cv.CV_32FC1)
    # for (x,y) in cv.GoodFeaturesToTrack(frame_gray, eig_image, temp_image, 4, 0.04, 200.0, useHarris = True):
    #     cv.Circle(frame, (int(x), int(y)), 10, cv.CV_RGB(255, 255, 255), 1)
    #     print "good feature at", x,y

    # cv.ShowImage("w2", frame)

    cv.ShowImage("w1", pFrame)
    c = cv.WaitKey(10)

def main():
    while True:
        repeat()

if __name__ == "__main__":
    main()
