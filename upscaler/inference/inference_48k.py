from __future__ import absolute_import, division, print_function, unicode_literals
import sys
# sys.path.append("..") # Removed - breaks package imports
import glob
import os
import argparse
import json
from re import S
import torch
import numpy as np
import torchaudio
import time
import torchaudio.functional as aF
from ..env import AttrDict # Use relative import
from ..datasets.dataset import amp_pha_stft, amp_pha_istft # Use relative import
from ..models.model import APNet_BWE_Model # Use relative import
import soundfile as sf
import matplotlib.pyplot as plt
from rich.progress import track

h = None
device = None

def load_checkpoint(filepath, device):
    assert os.path.isfile(filepath)
    print("Loading '{}'".format(filepath))
    checkpoint_dict = torch.load(filepath, map_location=device)
    print("Complete.")
    return checkpoint_dict

def scan_checkpoint(cp_dir, prefix):
    pattern = os.path.join(cp_dir, prefix + '*')
    cp_list = glob.glob(pattern)
    if len(cp_list) == 0:
        return ''
    return sorted(cp_list)[-1]

def inference(a):
    model = APNet_BWE_Model(h).to(device)

    state_dict = load_checkpoint(a.checkpoint_file, device)
    model.load_state_dict(state_dict['generator'])

    test_indexes = os.listdir(a.input_wavs_dir)

    os.makedirs(a.output_dir, exist_ok=True)

    model.eval()
    duration_tot = 0
    with torch.no_grad():
        for i, index in enumerate(track(test_indexes)):
            # print(index)
            audio, orig_sampling_rate = torchaudio.load(os.path.join(a.input_wavs_dir, index))
            audio = audio.to(device)
            
            audio_hr = aF.resample(audio, orig_freq=orig_sampling_rate, new_freq=h.hr_sampling_rate)
            audio_lr = aF.resample(audio, orig_freq=orig_sampling_rate, new_freq=h.lr_sampling_rate)
            audio_lr = aF.resample(audio_lr, orig_freq=h.lr_sampling_rate, new_freq=h.hr_sampling_rate)
            audio_lr = audio_lr[:, : audio_hr.size(1)]

            pred_start = time.time()
            amp_nb, pha_nb, com_nb = amp_pha_stft(audio_lr, h.n_fft, h.hop_size, h.win_size)

            amp_wb_g, pha_wb_g, com_wb_g = model(amp_nb, pha_nb)

            audio_hr_g = amp_pha_istft(amp_wb_g, pha_wb_g, h.n_fft, h.hop_size, h.win_size)
            duration_tot += time.time() - pred_start

            output_file = os.path.join(a.output_dir, index)

            sf.write(output_file, audio_hr_g.squeeze().cpu().numpy(), h.hr_sampling_rate, 'PCM_16')

    print(duration_tot)

def main():
    print('Initializing Inference Process..')

    parser = argparse.ArgumentParser()
    parser.add_argument('--input_wavs_dir', default='test')
    parser.add_argument('--output_dir', default='../generated_files')
    parser.add_argument('--checkpoint_file', required=True)
    a = parser.parse_args()

    config_file = os.path.join(os.path.split(a.checkpoint_file)[0], 'config.json')
    with open(config_file) as f:
        data = f.read()

    global h
    json_config = json.loads(data)
    h = AttrDict(json_config)

    torch.manual_seed(h.seed)
    global device
    if torch.cuda.is_available():
        torch.cuda.manual_seed(h.seed)
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')

    inference(a)


if __name__ == '__main__':
    main()

