import numpy as np
from scipy.optimize import curve_fit

class ShotAnalyzer:
    def __init__(self):
        """Initialize the shot analyzer."""
        self.shots = []
        
    def fit_trajectory(self, trajectory):
        """Fit a parabolic curve to the ball trajectory."""
        if len(trajectory) < 3:
            return None
            
        x = np.array([p[0] for p in trajectory])
        y = np.array([p[1] for p in trajectory])
        
        def parabola(x, a, b, c):
            return a * x**2 + b * x + c
            
        try:
            popt, _ = curve_fit(parabola, x, y)
            return popt
        except:
            return None
    
    def detect_shot_outcome(self, trajectory, hoop_position):
        """Determine if the shot was made or missed."""
        if len(trajectory) < 3:
            return None
            
        # Get the last few points of the trajectory
        last_points = trajectory[-3:]
        
        # Simple heuristic: if the ball's path intersects with the hoop area
        # and the trajectory is descending, it's likely a make
        for point in last_points:
            if self._is_near_hoop(point, hoop_position):
                return "make"
                
        return "miss"
    
    def _is_near_hoop(self, point, hoop_position, threshold=50):
        """Check if a point is near the hoop."""
        x, y = point
        hx, hy = hoop_position
        return np.sqrt((x - hx)**2 + (y - hy)**2) < threshold
    
    def calculate_shot_stats(self):
        """Calculate shooting statistics."""
        if not self.shots:
            return {
                "total_shots": 0,
                "makes": 0,
                "misses": 0,
                "fg_percentage": 0.0
            }
            
        makes = sum(1 for shot in self.shots if shot["outcome"] == "make")
        total = len(self.shots)
        
        return {
            "total_shots": total,
            "makes": makes,
            "misses": total - makes,
            "fg_percentage": (makes / total) * 100 if total > 0 else 0.0
        } 