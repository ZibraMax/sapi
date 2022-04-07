from head import SAPInstance

executable_path = "./launcher.bat"
executable_path = "C:/Program Files/Computers and Structures/SAP2000 23/SAP2000.exe"
working_folder = 'C:/Users/david/Desktop/SAP API Andres/SBDs'
O = SAPInstance(executable_path=executable_path,
                working_folder=working_folder, version=23, running_instance=True, verbose=True)
O.init()
O.fast_example()
O.SapModel.File.Save(O.modelPath)
