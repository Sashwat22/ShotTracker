# File: src/stats.py
from collections import deque
import time
from typing import Dict

class ShotStats:
    """
    Tracks shot attempts, makes, percentages, arc heights, and flight times.
    """
    def __init__(self):
        self.attempts = 0
        self.makes = 0
        self.threes_attempts = 0
        self.threes_makes = 0
        self.arc_heights = []
        self.flight_times = []
        # state machine per shot_id
        self.states: Dict[int, str] = {}  # FLYING, IN_RIM, BELOW_RIM
        self.start_time: Dict[int, float] = {}

    def start_shot(self, shot_id: int):
        self.start_time[shot_id] = time.time()
        self.states[shot_id] = 'FLYING'

    def update(self, shot_id: int, center_y: int, rim_bbox: tuple):
        state = self.states.get(shot_id)
        y_bottom = rim_bbox[3]
        if state == 'FLYING' and center_y < rim_bbox[1]:
            self.states[shot_id] = 'IN_RIM'
        elif state == 'IN_RIM' and center_y > y_bottom:
            self.states[shot_id] = 'BELOW_RIM'
        elif state == 'BELOW_RIM':
            self.end_shot(shot_id, made=True)
        # if it falls below without IN_RIM -> miss
        elif state == 'FLYING' and center_y > y_bottom:
            self.end_shot(shot_id, made=False)

    def end_shot(self, shot_id: int, made: bool):
        self.attempts += 1
        if made:
            self.makes += 1
        # compute flight time
        ft = time.time() - self.start_time.pop(shot_id, time.time())
        self.flight_times.append(ft)
        # reset state
        self.states.pop(shot_id, None)

    def current_stats(self) -> dict:
        fg_pct = self.makes / self.attempts * 100 if self.attempts else 0
        return {
            'Attempts': self.attempts,
            'Makes': self.makes,
            'FG%': fg_pct,
            '3PA': self.threes_attempts,
            '3P%': (self.threes_makes / self.threes_attempts * 100) if self.threes_attempts else 0,
            'Avg Flight Time': sum(self.flight_times)/len(self.flight_times) if self.flight_times else 0,
        }