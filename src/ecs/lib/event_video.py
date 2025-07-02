import os
import cv2
import numpy as np

from ecs.lib.dat import DatFile

class EventVideo():
    def __init__(self, cfg):
        self.cfg = cfg
        self.dat = DatFile(os.path.join(self.cfg.render.out, self.cfg.render.event_file))

    def create(self):
        ts, x, y, p = self.dat.load()

        res = self.cfg.event_camera.resolution
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')

        out_file = os.path.join(self.cfg.render.out, self.cfg.render.event_video_file)
        out = cv2.VideoWriter(out_file, fourcc, 20.0, (res[0], res[1]))

        tw = 1000
        img         = np.zeros((res[1], res[0]), dtype=float)
        tsurface    = np.zeros((res[1], res[0]), dtype=np.int64)
        indsurface  = np.zeros((res[1], res[0]), dtype=np.int8)


        for t in range(ts[0], ts[-1], tw):
            # Get events in the current time window
            ind = np.where((ts > t) & (ts < t + tw))

            # Create a matrix holding the time stamps of the events
            tsurface[:, :] = 0
            tsurface[y[ind], x[ind]] = t + tw

            # And another holding their polarity (use -1 for OFF events)
            indsurface[y[ind], x[ind]] = 2.0 * p[ind] - 1

            # Find which pixels to process
            ind = np.where(tsurface > 0)

            # And update the image
            img[:, :] = 125
            img[ind] = 125 + indsurface[ind] * np.exp(-(t + tw - tsurface[ind].astype(np.float32))/ (tw/30)) * 125

            # Convert to color and display
            img_c = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_GRAY2BGR)
            img_c = cv2.putText(img_c, '{} us'.format(t + tw), (0, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (255, 255, 255))
            img_c = cv2.applyColorMap(img_c, cv2.COLORMAP_VIRIDIS)
            cv2.imshow("debug", img_c)
            cv2.waitKey(1)
            
            # Write video to file
            out.write(img_c)
        out.release()