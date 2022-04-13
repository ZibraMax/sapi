from pysapi import *
import numpy as np
executable_path = "./launcher.bat"
working_folder = 'C:/Users/Arturo Rodriguez/Desktop/sapi/SBDs'
O = SAPInstance(executable_path=executable_path,
                working_folder=working_folder, version=19, running_instance=True, verbose=True)

O.init(start_new=True)

if O.SapModel.GetModelIsLocked():
    O.SapModel.SetModelIsLocked(False)


PinSupport = [True, True, True, False, False, False]
PatinSupport = [False, False, True, False, False, False]
FixedSupport = [True, True, True, True, True, True]
FreeNode = [False, False, False, False, False, False]
restraints = [
    PinSupport,
    PatinSupport,
    FreeNode,
    FreeNode,
    PatinSupport,
    PatinSupport,
]

W1 = 0.5
W2 = 0.5
W3 = 0.5
F1 = 0.5
F2 = 0.5
F3 = 0.5
F4 = 0.5

L1 = 1.0
L2 = 1.0
L3 = 1.0
L4 = 1.0
M1 = 1.0

FrameName1, ret = O.SapModel.FrameObj.AddByCoord(
    0, 0, 0, L1, 0, L4, "")
print(FrameName1, ret)
FrameName2, ret = O.SapModel.FrameObj.AddByCoord(
    L1, 0, L4, L1+L2, 0, L4, "")
print(FrameName2, ret)
FrameName3, ret = O.SapModel.FrameObj.AddByCoord(
    L1+L2, 0, L4, L1+L2+L3, 0, L4, "")
print(FrameName3, ret)
FrameName4, ret = O.SapModel.FrameObj.AddByCoord(
    L1+L2+L3, 0, L4, L1+L2+L3+L2, 0, L4, "")
print(FrameName4, ret)
FrameName5, ret = O.SapModel.FrameObj.AddByCoord(
    L1+L2+L3+L2, 0, L4, L1+L2+L3+L2+L1, 0, L4+L4, "")
print(FrameName5, ret)

count, names, res = O.SapModel.PointObj.GetNameList()
for i, nodo in enumerate(names):
    _, ret = O.SapModel.PointObj.SetRestraint(nodo, restraints[i])
    print(ret)

ret = O.SapModel.LoadPatterns.Add('CARGAS', 2, 0.0, True)
ret = O.SapModel.PointObj.SetLoadForce(
    names[1], 'CARGAS', [0.0, 0.0, -F2, 0.0, 0.0, 0.0])
ret = O.SapModel.PointObj.SetLoadForce(
    names[5], 'CARGAS', [-F4, 0.0, 0.0, 0.0, 0.0, 0.0])

ret = O.SapModel.FrameObj.SetLoadDistributed(
    FrameName1, 'CARGAS', 1, 10, 0, 1, W1, W1)
ret = O.SapModel.FrameObj.SetLoadDistributed(
    FrameName2, 'CARGAS', 1, 10, 0, 1, W2, W2)
ret = O.SapModel.FrameObj.SetLoadDistributed(
    FrameName3, 'CARGAS', 1, 10, 0, 1, W2, W2)
ret = O.SapModel.FrameObj.SetLoadDistributed(
    FrameName4, 'CARGAS', 1, 10, 0, 1, W2, W2)
ret = O.SapModel.FrameObj.SetLoadDistributed(
    FrameName5, 'CARGAS', 1, 10, 0, 1, W3, W3)


ret = O.SapModel.FrameObj.SetOutputStations(FrameName1, 2, -1, 101)
ret = O.SapModel.FrameObj.SetOutputStations(FrameName2, 2, -1, 101)
ret = O.SapModel.FrameObj.SetOutputStations(FrameName3, 2, -1, 101)
ret = O.SapModel.FrameObj.SetOutputStations(FrameName4, 2, -1, 101)
ret = O.SapModel.FrameObj.SetOutputStations(FrameName5, 2, -1, 101)

ret = O.SapModel.FrameObj.SetLoadPoint(FrameName1, 'CARGAS', 1, 10, 0.5, F1)
ret = O.SapModel.FrameObj.SetLoadPoint(
    FrameName3, 'CARGAS', 1, 10, 1/3, F3, Replace=False)
ret = O.SapModel.FrameObj.SetLoadPoint(
    FrameName3, 'CARGAS', 1, 10, 2/3, F3, Replace=False)
ret = O.SapModel.FrameObj.SetLoadPoint(
    FrameName3, 'CARGAS', 2, 5, 0.5, -M1, Replace=False)

Tipo4 = [[False, False, False, False, False, True], [
    False, False, False, False, False, True], [0.0]*6], [0.0]*6

O.SapModel.FrameObj.SetReleases(FrameName3, [False, False, False, False, False, True], [
                                False, False, False, False, False, True], [0.0]*6, [0.0]*6)
O.SapModel.View.RefreshView(0, False)

O.SapModel.File.Save(O.modelPath)
O.SapModel.Analyze.RunAnalysis()


ret = O.SapModel.Results.Setup.DeselectAllCasesAndCombosForOutput()
ret = O.SapModel.Results.Setup.SetCaseSelectedForOutput('CARGAS')


table = [['frame', 'P0', 'P0.25', 'P0.5', 'P0.75', 'P1', 'V0', 'V0.25',
          'V0.5', 'V0.75', 'V1', 'M0', 'M0.25', 'M0.5', 'M0.75', 'M1']]
frames = [FrameName1, FrameName2, FrameName3, FrameName4, FrameName5]
for frame in frames:
    NumberResults, Obj, ObjSta, Elm, ElmSta, LoadCase, StepType, StepNum, P, V2, V3, T, M2, M3, ret = O.SapModel.Results.FrameForce(
        frame, 0)
    L = ElmSta[-1]
    P0, P025, P05, P075, P1 = np.interp(
        np.array([0.0, 0.25, 0.5, 0.75, 1.0])*L, ElmSta, P)
    V0, V025, V05, V075, V1 = np.interp(
        np.array([0.0, 0.25, 0.5, 0.75, 1.0])*L, ElmSta, V2)
    M0, M025, M05, M075, M1 = np.interp(
        np.array([0.0, 0.25, 0.5, 0.75, 1.0])*L, ElmSta, M3)
    table += [[frame, P0, P025, P05, P075, P1, V0, V025,
               V05, V075, V1, M0, M025, M05, M075, M1]]
np.savetxt('Results.csv', table, delimiter=',', fmt='%s')
