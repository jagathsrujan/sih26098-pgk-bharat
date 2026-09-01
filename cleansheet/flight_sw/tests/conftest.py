import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FLIGHT_SW = os.path.dirname(HERE)
CLEANSHEET = os.path.dirname(FLIGHT_SW)
sys.path.insert(0, FLIGHT_SW)
sys.path.insert(0, os.path.join(CLEANSHEET, "scripts"))
