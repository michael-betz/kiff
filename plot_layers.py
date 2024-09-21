#!/usr/bin/env python
'''
Plot a selection of layers of a kicad pcb as .pdf files
'''
import sys
import pcbnew
import os


def plot_layers(f_name, plot_dir, layers=['F.Cu', 'B.Cu'], zone_refill=True):
    '''
    f_name: the .kicad_pcb file to plot
    plot_dir: output directory for the .pdf files
    layers: list of layer names to plot
    zone_refill: if True, re-calculate copper fills before plotting
    returns: dict with coordinates of bounding box containing the PCB [inches]
    '''
    if not os.path.isfile(f_name) or not os.access(f_name, os.R_OK):
        print("%s: not readable, aborting" % f_name)
        return None
    try:
        board = pcbnew.LoadBoard(f_name)
    except Exception:
        print("%s: failed to load with pcbnew, aborting" % f_name)
        return None
    # after this point, chances of failure are low

    if zone_refill:
        print('filling zones ...')
        zf = pcbnew.ZONE_FILLER(board)
        zf.Fill(board.Zones())

    boardbox = board.ComputeBoundingBox()
    bounds = {
        'x': boardbox.GetX() / 1e6 / 25.4,
        'y': boardbox.GetY() / 1e6 / 25.4,
        'W': boardbox.GetWidth() / 1e6 / 25.4,
        'H': boardbox.GetHeight() / 1e6 / 25.4,
    }
    # print('bounds [inch]:', bounds)

    pctl = pcbnew.PLOT_CONTROLLER(board)
    # pctl.SetColorMode(True)

    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(plot_dir)
    popt.SetPlotFrameRef(False)
    # popt.SetLineWidth(pcbnew.FromMM(0.15))
    # popt.SetAutoScale(False)
    popt.SetScale(1)
    popt.SetMirror(False)
    # popt.SetUseGerberAttributes(True)
    # popt.SetExcludeEdgeLayer(False)
    # popt.SetUseAuxOrigin(True)
    # popt.SetDrillMarksType(popt.FULL_DRILL_SHAPE)

    for layer in layers:
        pctl.SetLayer(board.GetLayerID(layer))
        pctl.OpenPlotfile(layer, pcbnew.PLOT_FORMAT_PDF, layer)
        pctl.PlotLayer()
        pctl.ClosePlot()

    return bounds


if __name__ == "__main__":
    boardName = sys.argv[1]
    plot_dir = sys.argv[2]
    plot_layers(boardName, plot_dir)
