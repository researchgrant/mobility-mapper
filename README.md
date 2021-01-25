# mobility-mapper

This app allows allows for the scoring of behavioral videos involving mobility (or any other binary behavior). The behavior state is stored for each frame of the video to allow for in depth analysis. Total time immobile and latency to immobility are calculated in the app, but the raw fame-wise state data can also be saved to excel for further analysis.
This app is ideal for manual scoring of behaviors in preparation for training automated bahavior detection using machine learning and DeepLabCut.

Manually intalling dependencies:

Pip install opencv-python
Conda install qtpy
Conda install qtpygraph

Download fst_dist3.py and fsw.py in the same folder

Run in IDE or launch in terminal with:
python fst_dist3.py
