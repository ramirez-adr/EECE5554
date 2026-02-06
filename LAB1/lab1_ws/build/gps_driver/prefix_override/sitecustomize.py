import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/parallels/Desktop/EECE5554/LAB1/lab1_ws/install/gps_driver'
