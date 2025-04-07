from dvs_sensor import *
# import iebcs

# iebcs.initSimu(200, 200)
# iebcs.initLatency(100.0, 30.0, 100.0, 1000.0)
# iebcs.initContrast(0.3, 0.6, 0.035)

# init_bgn_hist_cpp("../data/noise_pos_3klux.npy", "../data/noise_pos_3klux.npy")
# img = np.zeros((200, 200), dtype=np.uint8)
# img[:, :] = 125
# img[50:150, 50:150] = 150
# iebcs.initImg(img)
# img[:, :] = 125
# img[55:155, 55:155] = 170
# s = iebcs.updateImg(img, 46000)
# print(s)
# s = iebcs.getShape()
# print(s)
# s = iebcs.getCurv()
# print(s)
# print("Test completed")

import dsi
from dvs_sensor import *

def main():
    dsi.initSimu(200, 200)
    dsi.initLatency(100.0, 30.0, 100.0, 1000.0)
    dsi.initContrast(0.3, 0.6, 0.035)

    init_bgn_hist_cpp("data/noise_neg_3klux.npy", "data/noise_neg_3klux.npy")
    img = np.zeros((200, 200), dtype=np.uint8)
    img[:, :] = 125
    img[50:150, 50:150] = 150
    dsi.initImg(img)
    img[:, :] = 125
    img[55:155, 55:155] = 170
    s = dsi.updateImg(img, 46000)
    print(s)
    s = dsi.getShape()
    print(s)
    s = dsi.getCurv()
    print(s)
    print("Test completed")


    print('done')