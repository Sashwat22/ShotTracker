from PyQt5.QtWidgets import QLabel, QGridLayout, QGroupBox, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase, QFont

class StatsDisplay:
    def __init__(self, parent=None):
        self.parent = parent
        
        # Shot result flash settings
        self.shot_made_flash_duration = 15
        self.shot_miss_flash_duration = 15
        self.shot_made_flash = 0
        self.shot_miss_flash = 0
        self.previous_shot_outcome = None
        
        # Create statistics group layout
        self.stats_group = QGroupBox("STATISTICS")
        self.stats_layout = self._create_stats_layout()
        self.stats_group.setLayout(self.stats_layout)
        
    def _create_stats_layout(self):
        """Create the statistics display layout"""
        stats_layout = QGridLayout()
        stats_layout.setVerticalSpacing(12)
        stats_layout.setHorizontalSpacing(20)

        # Define styles
        font_size = "font-size: 14px;"
        self.label_style = f"color: #AAAAAA; {font_size}"
        self.value_style = f"color: #FFFFFF; font-weight: bold; {font_size}"
        
        # Shot Result Label - Make it more prominent
        row = 0
        self.result_label = QLabel("AWAITING SHOT")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setFont(QFont("Roboto Condensed", 18) if "Roboto Condensed" in QFontDatabase().families() else QFont("Arial", 18, QFont.Bold))
        self.result_label.setStyleSheet("color: #FFFFFF; margin-bottom: 10px; font-weight: bold;")
        stats_layout.addWidget(self.result_label, row, 0, 1, 2)
        row += 1
        
        # Create the statistics fields
        self.fields = {}
        
        # Made/Attempted
        self.fields['made'] = self._add_stat_field(stats_layout, row, "Made/Attempted:", "0/0")
        row += 1
        
        # Success Rate
        self.fields['percentage'] = self._add_stat_field(stats_layout, row, "Success Rate:", "0.00%")
        row += 1
        
        # Launch Angle
        self.fields['arc'] = self._add_stat_field(stats_layout, row, "Launch Angle:", "N/A")
        row += 1
        
        # Current Speed
        self.fields['speed'] = self._add_stat_field(stats_layout, row, "Current Speed:", "N/A")
        row += 1
        
        # Shot Average Speed
        self.fields['avg_speed'] = self._add_stat_field(stats_layout, row, "Shot Average Speed:", "N/A")
        row += 1
        
        # Distance to Hoop
        self.fields['distance'] = self._add_stat_field(stats_layout, row, "Distance to Hoop:", "N/A")
        row += 1
        
        # Status
        self.fields['status'] = self._add_stat_field(stats_layout, row, "Status:", "No video loaded.")
        row += 1
        
        # Set column stretch for values 
        stats_layout.setColumnStretch(1, 1)
        
        return stats_layout
        
    def _add_stat_field(self, layout, row, label_text, initial_value):
        """Add a stat field with label and value to the layout"""
        label = QLabel(label_text)
        label.setStyleSheet(self.label_style)
        
        value_label = QLabel(initial_value)
        value_label.setStyleSheet(self.value_style)
        
        layout.addWidget(label, row, 0)
        layout.addWidget(value_label, row, 1)
        
        return value_label
        
    def get_group(self):
        """Return the stats group widget"""
        return self.stats_group
        
    def update_stats(self, stats=None, arc_angle=None, inst_speed=None, avg_speed=None, hoop_dist=None):
        """Update the statistics display"""
        if stats:
            made, attempted = stats
            percentage = (made / attempted * 100) if attempted > 0 else 0
            self.fields['made'].setText(f"{made}/{attempted}")
            self.fields['percentage'].setText(f"{percentage:.2f}%")
            
        if arc_angle is not None:
            self.fields['arc'].setText(f"{arc_angle:.1f}°")
            
        if inst_speed is not None:
            self.fields['speed'].setText(f"{inst_speed:.0f} px/s")
            
        if avg_speed is not None:
            self.fields['avg_speed'].setText(f"{avg_speed:.0f} px/s")
            
        if hoop_dist is not None:
            self.fields['distance'].setText(f"{hoop_dist:.0f} px")
            
    def set_status(self, status_text):
        """Set the status text"""
        self.fields['status'].setText(status_text)
        
    def set_result(self, result_text, is_made=None):
        """Set the shot result text and styling"""
        self.result_label.setText(result_text)
        
        if is_made is True:
            self.result_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 20px;")
            self.shot_made_flash = self.shot_made_flash_duration
            self.shot_miss_flash = 0
            self.previous_shot_outcome = "MADE"
            print(f"Shot made flash set to {self.shot_made_flash}")
        elif is_made is False:
            self.result_label.setStyleSheet("color: #F44336; font-weight: bold; font-size: 20px;")
            self.shot_miss_flash = self.shot_miss_flash_duration
            self.shot_made_flash = 0
            self.previous_shot_outcome = "MISSED"
            print(f"Shot miss flash set to {self.shot_miss_flash}")
        else:
            self.result_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 18px;")
            
    def reset_stats(self):
        """Reset all statistics"""
        self.fields['made'].setText("0/0")
        self.fields['percentage'].setText("0.00%")
        self.fields['arc'].setText("N/A")
        self.fields['speed'].setText("N/A")
        self.fields['avg_speed'].setText("N/A")
        self.fields['distance'].setText("N/A")
        self.fields['status'].setText("Ready")
        self.set_result("AWAITING SHOT")
        
        # Reset flash counters and previous outcome
        self.shot_made_flash = 0
        self.shot_miss_flash = 0
        self.previous_shot_outcome = None
        
        print("Statistics display reset")
        
    def get_flash_status(self):
        """Get current flash status for visualization"""
        if self.shot_made_flash > 0:
            self.shot_made_flash -= 1
            print(f"Made flash active: {self.shot_made_flash}")
            return "MADE", self.shot_made_flash
        elif self.shot_miss_flash > 0:
            self.shot_miss_flash -= 1
            print(f"Miss flash active: {self.shot_miss_flash}")
            return "MISSED", self.shot_miss_flash
        else:
            return None, 0 