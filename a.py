from head import SAPInstance

executable_path = "./launcher.bat"
working_folder = 'C:/Users/david/Desktop/SAP API Andres/SBDs'
O = SAPInstance(executable_path=executable_path,
                working_folder=working_folder, running_instance=False, verbose=True)
O.init()
O.fast_example()
O.SapModel.File.Save(O.modelPath)
