import matplotlib.pyplot as plt
from pysapi import *
import numpy as np

executable_path = "./launcher.bat"
working_folder = 'C:/Users/Arturo Rodriguez/Desktop/sapi/SBDs'
O = SAPInstance(executable_path=executable_path,
                working_folder=working_folder,
                version=19,
                running_instance=True,
                filename='puchober.sdb',
                verbose=True)

O.init(start_new=False)

GRUPOS = ['VIGAS_PISO_1', 'VIGAS_PISO_2']
SECCIONES_DEFECTUOSAS = ['Vigas_defecto_1', 'Vigas_defecto_2',
                         'Vigas_defecto_3', 'Vigas_defecto_4']

DESPLAZAMIENTOS_CUBIERTA = []
REACCIONES_BASE = []
O.SapModel.Analyze.RunAnalysis()
ret = O.SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
ret = O.SapModel.Results.Setup.SetCaseSelectedForOutput('PO')
_, _, _, _, Fx, _, _, _, _, _, _, _, _, ret = O.SapModel.Results.BaseReact()
_, _, _, _, _, _, U1, _, _, _, _, _, ret = O.SapModel.Results.JointDispl(
    '15', 0)

DESPLAZAMIENTOS_CUBIERTA += [U1]
REACCIONES_BASE += [Fx]
O.SapModel.SetModelIsLocked(False)
cot = 0
lencot = len(GRUPOS)*len(SECCIONES_DEFECTUOSAS)
for grupo in GRUPOS:
    for seccion in SECCIONES_DEFECTUOSAS:
        cot += 1
        logging.info(f'Corriendo con {grupo} {seccion} {(cot/lencot):.3f}')
        ret = O.SapModel.FrameObj.SetSection(grupo, seccion, 1)
        if not ret == 0:
            logging.error('ALGO PASO AL CAMBIAR LA SECCIÓN TRANSVERSAL', ret)

        O.SapModel.Analyze.RunAnalysis()
        _, _, _, _, Fx, _, _, _, _, _, _, _, _, ret1 = O.SapModel.Results.BaseReact()
        _, _, _, _, _, _, U1, _, _, _, _, _, ret2 = O.SapModel.Results.JointDispl(
            '15', 0)
        if not ret1 == 0 or not ret2 == 0:
            logging.error('NO SE PUDO COMPLETAR EL ANALISIS')
        else:
            DESPLAZAMIENTOS_CUBIERTA += [U1]
            REACCIONES_BASE += [Fx]

        O.SapModel.SetModelIsLocked(False)
for i in range(1, len(REACCIONES_BASE)):
    U1 = DESPLAZAMIENTOS_CUBIERTA[i]
    Fx = REACCIONES_BASE[i]
    plt.plot(U1, abs(np.array(Fx)), c='gray')
U1 = DESPLAZAMIENTOS_CUBIERTA[0]
Fx = REACCIONES_BASE[0]
plt.plot(U1, abs(np.array(Fx)), c='k', linewidth=3)
plt.grid()
plt.xlabel('Desplazamiento monitorizado [m]')
plt.ylabel('Reacción de cortante en la base [|kN|]')
plt.title('Análisis estático no lineal')
plt.show()
a = 0
