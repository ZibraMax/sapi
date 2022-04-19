import os
import sys
import comtypes.client
from .FEMLogger import FEMLogger
import logging


class SAPInstance():
    """docstring for SAPInstance
    """

    def __init__(self, executable_path, working_folder='./temp', version=19, running_instance=False, filename='', verbose=False):
        self.executable_path = executable_path
        self.working_folder = working_folder
        self.running_instance = running_instance
        self.filename = filename or "temp.sdb"
        self.version = version
        self.logger = FEMLogger()
        console_log_level = "warning" if not verbose else "info"
        self.logger.setup_logging(console_log_level=console_log_level)

        if not os.path.exists(self.working_folder):
            try:
                os.makedirs(self.working_folder)
                logging.info(f"Working folder {self.working_folder} created.")
            except OSError:
                logging.info(
                    f"Working folder {self.working_folder} already created.")

        self.modelPath = os.path.join(self.working_folder, self.filename)

    def saveFileCustomName(self, customName):
        modelPath = os.path.join(self.working_folder, customName)
        self.SapModel.File.Save(modelPath)

    def init(self, start_new=True):
        if self.running_instance:
            try:
                self.mySapObject = comtypes.client.GetActiveObject(
                    "CSI.SAP2000.API.SapObject")
                logging.info("Running instance found!")
            except (OSError, comtypes.COMError):
                logging.error(
                    "No running instance of the program found or failed to attach. Trying to start a new window")
                self.running_instance = False
                self.init()
                return None
        else:
            if self.version == 19:
                helper = comtypes.client.CreateObject('SAP2000v19.Helper')
                helper = helper.QueryInterface(comtypes.gen.SAP2000v19.cHelper)
            elif self.version == 23:
                helper = comtypes.client.CreateObject('SAP2000v1.Helper')
                helper = helper.QueryInterface(comtypes.gen.SAP2000v1.cHelper)
            try:
                self.mySapObject = helper.CreateObject(self.executable_path)
                logging.info("SAP2000 Executable found!")
            except (OSError, comtypes.COMError):
                logging.error(
                    f"Cannot start a new instance of the program from {self.executable_path}")
                sys.exit(-1)
            self.mySapObject.ApplicationStart()
        self.SapModel = self.mySapObject.SapModel
        if start_new:
            self.SapModel.InitializeNewModel()
            self.SapModel.File.NewBlank()
        self.SapModel.SetPresentUnits(6)  # SapModel.SetPresentUnits(KN_m_C)
