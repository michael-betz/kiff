#!/usr/bin/env python2

'''
Plot a selection of layers of a kicad pcb as .pdf files
'''

import sys
import pcbnew


def plot_layers(f_name, plot_dir, layers=['F.Cu', 'B.Cu'], zone_refill=True):
    board = pcbnew.LoadBoard(f_name)

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
    popt.SetExcludeEdgeLayer(False)
    # popt.SetUseAuxOrigin(True)pctl.SetColorMode(False)

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
