#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2026 talYaliStav.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr
import matplotlib
matplotlib.use('Agg') # MUST be called before importing pyplot
import matplotlib.pyplot as plt

class theBestBlock(gr.sync_block):
    """
    docstring for block theBestBlock
    """
    def __init__(self, samples_len, epsilon, fs, norm_factor):
        gr.sync_block.__init__(self,
            name="theBestBlock",
            in_sig=[np.complex64, ],
            out_sig=None)
        self.samples_len = int(samples_len)
        self.epsilon = epsilon
        self.fs = fs
        self.norm_factor = norm_factor
        self.backward = False
        self.forward = False
        self.threshold = 26
        # self.flag = True
        self.pos_counter = 0
        self.neg_counter = 0
        self.last_printed = ""
        self.stable_move = 3


    def work(self, input_items, output_items):
        in0 = input_items[0]
        
        shifted_signal = in0[:self.samples_len]

        # N_fft is the total size of the FFT (samples + zeros)
        # Increasing this gives you "narrower" bins (better resolution)
        padding_factor = 8 # 8x interpolation
        n_fft = self.samples_len * padding_factor

        # 2. Compute FFT and shift zero-frequency component to center
        fft_data = np.fft.fftshift(np.fft.fft(shifted_signal, n = n_fft))
        
        # 3. Apply threshold (epsilon) to filter noise
        # We work with magnitudes (amplitudes)
        amplitudes = np.abs(fft_data)
        amplitudes[amplitudes < self.epsilon] = 0

        # 4. Define frequency bins
        # fftfreq returns bins from -fs/2, fs/2
        freqs = np.fft.fftshift(np.fft.fftfreq(n_fft, 1/self.fs))

        # 5. Compare positive vs negative frequency energy
        pos_mask = (freqs > self.norm_factor) & (freqs <= 1.175 * self.norm_factor)
        neg_mask = (freqs < self.norm_factor) & (freqs >= 165)

        # 5. Energy Calculation within the windowed range
        pos_energy = np.sum(amplitudes[pos_mask])
        neg_energy = np.sum(amplitudes[neg_mask])
        
        # if self.flag:
        #     # 2. Plotting
        #     plt.figure(figsize=(10, 4))
        #     plt.scatter(freqs[int(n_fft / 3) : int(2 * n_fft / 3)], amplitudes[int(n_fft / 3) : int(2 * n_fft / 3)])
        #     plt.savefig('latest_spectrum.png') # Save to disk
        #     plt.close() # CRITICAL: Free memory or you will leak RAM and crash
        #     self.flag = False
            
        # print(f"Strength Positive is {pos_energy}")
        # print(f"Strength Negative is {neg_energy}")

        # 6. Direction Logic
        if pos_energy > neg_energy and pos_energy > self.threshold:
            self.pos_counter += 1
            self.neg_counter = 0
            if (not self.forward) and (self.pos_counter == self.stable_move) and (not self.last_printed == "Forward"):
                print(f"Forward: Towards Antenna (Strength: {pos_energy:.2f})")
                self.forward = True
                self.backward = False
                self.last_printed = "Forward"

        elif neg_energy > pos_energy and neg_energy > self.threshold:
            self.neg_counter += 1
            self.pos_counter = 0
            if (not self.backward) and (self.neg_counter == self.stable_move) and (not self.last_printed == "Backward"):
                print(f"Backward: Away from Antenna (Strength: {neg_energy:.2f})")
                self.backward = True
                self.forward = False
                self.last_printed = "Backward"
        
        else:
            # print("No significant movement detected")
            self.backward = False
            self.forward = False
            # self.pos_counter = 0
            # self.neg_counter = 0

        # Consume the processed samples
        return self.samples_len
