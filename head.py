import os
import sys
import comtypes.client
from FEMLogger import FEMLogger
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

    def load_section(self, filename):
        with open(filename, 'r') as f:
            logging.info(f"{filename} loaded")

            lines = f.read().splitlines()
            sec_name = lines[0].split(',')[0]
            sec_type = lines[0].split(',')[1]
            mat = lines[0].split(',')[-1]

            name = lines[-1]
            ec = self.SapModel.PropFrame.SetSDSection(name, mat)
            logging.info(f"{name} created. Exit code {ec}")

            if sec_type == 'RECT':
                b, h = [float(i) for i in lines[0].split(',')[2:-1]]
                sec_name, ec = self.SapModel.PropFrame.SDShape.SetSolidRect(
                    name, sec_name, mat, "Default", 0, 0, h, b, 0, -1)
                logging.info(f"Rect {sec_name}. Exit code {ec}")
                cx = h/2
                cy = h/2
            elif sec_type == 'CIRC':
                r = float(lines[0].split(',')[2])
            n = len(lines)
            for i in range(1, n-1):
                line = lines[i].split(',')
                rebar_name, x, y, number, rebar_mat = [line[0], float(line[1]), float(
                    line[2]), line[3], line[4]]

                rebar_name, ec = self.SapModel.PropFrame.SDShape.SetReinfSingle(
                    name, '', x-cx, y-cy, number, rebar_mat)
                logging.info(f"Rebar {rebar_name}. Exit code {ec}")
                self.SapModel.PropFrame.SDShape.GetReinfSingle(
                    name, rebar_name)

    def load_material(self, filename):
        with open(filename, 'r') as f:
            lines = f.read().splitlines()
            if lines[0] == "QUICK":
                name, mat_type, m1, m2, m3, m4, m5, m6, cus_name = lines[1:]
                mat_type = int(mat_type)
                m1 = int(m1)
                m2 = int(m2)
                m3 = int(m3)
                m4 = int(m4)
                m5 = int(m5)
                m6 = int(m6)
                name, s = self.SapModel.PropMaterial.AddQuick(
                    name, mat_type, m1, m2, m3, m4, m5, m6, cus_name)
                logging.info(f"Material {name}, exit code {s}")

    def fast_example(self):
        self.SapModel.File.New2DFrame(0, 3, 3.5, 4, 3.2)
        self.load_material('Concrete1.txt')
        self.load_material('R1.txt')
        self.load_section('section.txt')

    def fast_example2(self):
        self.SapModel.File.New2DFrame(0, 2, 144, 2, 288)
        rebar_material_name, ec = self.SapModel.PropMaterial.AddQuick(
            'REBAR_MATERIAL', 6, -1, -1, -1, -1, 4)
        ec = self.SapModel.PropFrame.SetSDSection("SD1", "4000psi")
        rname, ec = self.SapModel.PropFrame.SDShape.SetReinfSingle(
            "SD1", "SH1", 5, 5, "#9", rebar_material_name)
        logging.info(f'{rname},{ec}')
