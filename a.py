from head import SAPInstance
import matplotlib.pyplot as plt


areas = []
p = []

executable_path = "./launcher.bat"
executable_path = "C:/Program Files/Computers and Structures/SAP2000 23/SAP2000.exe"
working_folder = 'C:/Users/david/Desktop/SAP API Andres/SBDs'
O = SAPInstance(executable_path=executable_path,
                working_folder=working_folder, version=23, running_instance=True, verbose=True)
O.init(start_new=False)

frame_obj = "1"


O.SapModel.File.Save(O.modelPath)
O.SapModel.Analyze.RunAnalysis()

O.SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
O.SapModel.Results.Setup.SetCaseSelectedForOutput('Fb-CR')

res = O.SapModel.Results.FrameJointForce(frame_obj, 0)


plt.plot(areas, p)
plt.plot()
plt.show()
