from datetime import datetime
import logging
import os
from pathlib import Path

TIMESTAMP = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")

PROJECTDIR = Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute()
DATAFILE = "Atopische Dermatitis honden, versie 3 November.xlsm"

DATA_PATH = os.path.join(PROJECTDIR, "data/raw", DATAFILE)

# set log directory
logging.basicConfig(
    filename=os.path.join(PROJECTDIR, f"logs/{TIMESTAMP}.log"), level=logging.INFO
)
