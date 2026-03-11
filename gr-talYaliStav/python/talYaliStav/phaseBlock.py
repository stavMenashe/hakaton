#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2026 TalYaliStav.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#


import numpy as np
from gnuradio import gr

class phaseBlock(gr.sync_block):
    """
    docstring for block phaseBlock
    """
    def __init__(self, samples_len, epsilon, fs, norm_factor):
        gr.sync_block.__init__(self,
            name="phaseBlock",
            in_sig=[np.complex64, ],
            out_sig=None)
        self.samples_len = samples_len
        self.epsilon = epsilon
        self.fs = fs
        self.norm_factor = norm_factor
        self.acc_buffer = []
        self.block_rate = self.fs / self.samples_len
        self.history_size = int(self.block_rate * 8.0)
        self.dphi_history = np.zeros(self.history_size, dtype = np.float32)
        self.history_idx = 0
        self.history_full = False
        self.last_phase = None
        self.breath_stable_cnt = 0
        self.breath_threshold = 0.04
        self.min_amplitude = 0.001
        self.dc_alpha = 0.95
        self.dc_offset = 0j


    def work(self, input_items, output_items):
        in0 = input_items[0]
        
        self.acc_buffer.extend(in0)
        if len(self.acc_buffer) > self.samples_len * 50:
            self.acc_buffer = self.acc_buffer[-self.samples_len:]
            
        while len(self.acc_buffer) >= self.samples_len:
            current_block = np.array(self.acc_buffer[:int(self.samples_len)], dtype=np.complex64)
            del self.acc_buffer[:int(self.samples_len)]
            
            block_mean = np.mean(current_block)
            block_amp = np.abs(block_mean)
            
            if block_amp < self.min_amplitude:
                self.last_phase = None
                self.breath_stable_cnt = 0
                self.history_full = False
                self.history_idx = 0
                self.dphi_history.fill(0)
                continue
            
            self.dc_offset = self.dc_alpha * self.dc_offset + (1 - self.dc_alpha) * block_mean
            centered_mean = block_mean - self.dc_offset
            
            current_phase = np.angle(block_mean)
            if self.last_phase is None:
                self.last_phase = current_phase
                continue
            
            dphi = (current_phase - self.last_phase + np.pi) % (2 * np.pi) - np.pi
            dphi = np.clip(dphi, -0.6, 0.6)
            self.last_phase = current_phase
            
            self.dphi_history[self.history_idx] = dphi
            self.history_idx = (self.history_idx + 1) % self.history_size
            if self.history_idx == 0:
                self.history_full = True
                
            if self.history_full and (self.history_idx % 10 == 0):
                dphi_vec = np.roll(self.dphi_history, -self.history_idx)
                dphi_vec -= np.mean(dphi_vec)
                
                phase_fft = np.abs(np.fft.rfft(dphi_vec))
                phase_freqs = np.fft.rfftfreq(self.history_size, 1 / self.block_rate)
                
                breath_mask = (phase_freqs >= 0.15) & (phase_freqs <= 0.6)
                breath_total_energy = np.sum(phase_fft[breath_mask])
                
                print("*")
                if breath_total_energy > self.breath_threshold:
                    self.breath_stable_cnt += 1

                    if self.breath_stable_cnt >= 3:
                        print(f"Breathing detected! (Energy: {breath_total_energy: .3f})")
                        self.breath_stable_cnt = 0
                    
    
        return len(in0)
