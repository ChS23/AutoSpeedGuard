import os
import tempfile

import streamlit as st
import cv2
from PIL import Image
from ultralytics import YOLO
from ultralytics.solutions import speed_estimation


def main():
    st.title("Speed Estimation App")
    st.text("Upload a video and get the speed of the vehicle in the video")

    upload_video = st.file_uploader("Upload a video", type=["mp4"])

    if upload_video:
        model = YOLO("../yolov8s.pt")
        names = model.names

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(upload_video.read())

        cap = cv2.VideoCapture(temp_file.name)
        assert cap.isOpened(), "Error reading video file"

        w, h, fps = (
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            cap.get(cv2.CAP_PROP_FPS),
        )

        video_writer = cv2.VideoWriter(
            "../output.avi",
            cv2.VideoWriter.fourcc(*"mp4v"),
            fps,
            (w, h),
        )

        line_pts = [
            [0, 0],
            [w, 0],
            [w, h],
            [0, h],
        ]

        speed_obj = speed_estimation.SpeedEstimator()
        speed_obj.set_args(
            reg_pts=line_pts,
            names=names,
            view_img=True,
            spdl_dist_thresh=1000,
        )

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.warning("Video frame is empty or video processing has been successfully completed.")
                break

            tracks = model.track(frame, persist=True)
            frame = speed_obj.estimate_speed(frame, tracks)

            if any(cls in [2, 7] for cls in speed_obj.clss):
                pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                st.image(pil_img, channels="RGB")

        cap.release()
        os.unlink(temp_file.name)
        video_writer.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
