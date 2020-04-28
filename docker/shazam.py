import os
import gc
import pickle
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json

import librosa
import numpy as np
from scipy.ndimage.filters import maximum_filter
import scipy.ndimage as ndimage


sample_rate = 9000
time_resolution = 0.005
target = (
    int(sample_rate*time_resolution),
    int(10*sample_rate*time_resolution),
    -50, 100
)    # start, end, low filter, high filter
score_threshold = 30
n_mels = 64
filter_size = (20, 20)
time_to_process = 30 # in seconds
time2fft = 0.2 # in seconds

def read_and_resample(path, sample_rate):
    y, sr = librosa.load(path, sr=sample_rate)
    return y


def form_constellation(name, wav, sample_rate, time2fft=0.2):
    window_size = int(sample_rate * time2fft)
    hop_length = int(sample_rate * time2fft / 4)
    S = librosa.feature.melspectrogram(
        wav,
        n_fft=window_size,
        hop_length=hop_length,
        n_mels=n_mels,

    )
    S = librosa.power_to_db(S, ref=np.min(S))

    Sb = maximum_filter(S, size=filter_size) == S

    Sbd, num_objects = ndimage.label(Sb)
    objs = ndimage.find_objects(Sbd)
    points = []
    for dy, dx in objs:
        x_center = (dx.start + dx.stop - 1) // 2
        y_center = (dy.start + dy.stop - 1) // 2
        if (dx.stop - dx.start) * (dy.stop - dy.start) == 1:
            points.append((x_center, y_center))

    return points


def build_constellation_index(constellation_collection, target,
                              show_progress=True):
    result_index = {}
    range_ = constellation_collection.items()
    if show_progress:
        range_ = tqdm(range_)
    for name, constellation in range_:
        constellation = np.array(constellation)
        for anchor in constellation:
            start_t = anchor[0] + target[0]
            stop_t = anchor[0] + target[1]
            min_f = anchor[1] + target[2]
            max_f = anchor[1] + target[3]

            mask = (
                    (constellation[:, 0] >= start_t) &
                    (constellation[:, 0] <= stop_t) &
                    (constellation[:, 1] >= min_f) &
                    (constellation[:, 1] <= max_f)
            )
            points = constellation[mask]
            for point in points:
                key = (anchor[1], point[1], point[0] - anchor[0])
                value = (anchor[0], name)
                if key in result_index:
                    result_index[key].append(value)
                else:
                    result_index[key] = [value]

    return result_index

def get_scores(index, request, score_threshold=50):
    intersected_keys = (index.keys() & request.keys())
    time_offsets = {}
    scores = {}
    offsets = {}
    for key in intersected_keys:
        for request_time, _ in request[key]:
            for index_time, matched_name in index[key]:
                delta_time = (index_time - request_time) // 5

                match = time_offsets.setdefault(matched_name, {})
                for delta in range(delta_time - 1, delta_time + 2):
                    if delta in match:
                        match[delta] += 1
                    else:
                        match[delta] = 1
    max_score_data = [None, 0, 0]
    for name in time_offsets.keys():
        offset, score = max(time_offsets[name].items(), key=lambda x: x[1])

        if score > score_threshold:
            if scores.get(name, 0) < score:
                scores[name] = score
                offsets[name] = offset
        if score > max_score_data[1]:
            max_score_data = [name, score, offset]
    if len(scores)==0:
        name, score, offset = max_score_data
        scores[name] = score
        offsets[name] = offset
    return scores, offsets

def predict(wav, index):
    name = "request"
    constellation = form_constellation(name, wav, sample_rate, time2fft)
    request_index = build_constellation_index(
        {
            name: constellation
        },
        target,
        show_progress=False
    )
    scores, offsets = get_scores(index, request_index)
    scores = list(scores.items())
    scores.sort(key=lambda x: -x[1])
    print(scores[:10])
    result = []
    for name, score in scores:
        data = {"Name":name, "Score":score}
        result.append(data)

    return result
