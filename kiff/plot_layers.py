#!/usr/bin/env python
"""
Plot a selection of layers of a kicad pcb as .pdf files

As of Kicad 8, almost the whole functionality of this script is integrated in
kicad-cli.
"""
import sys
import pcbnew
import os


def plot_layers(f_name, plot_dir, layers=["F.Cu", "B.Cu"], zone_refill=True):
    """
    f_name: the .kicad_pcb file to plot
    plot_dir: output directory for the .pdf files
    layers: list of layer names to plot
    zone_refill: if True, re-calculate copper fills before plotting
    returns: dict with coordinates of bounding box containing the PCB [inches]
    """
    try:
        version = int(pcbnew.Version().split(".")[0])
    except AttributeError:
        version = 5

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
        print("filling zones ...")
        zf = pcbnew.ZONE_FILLER(board)
        zf.Fill(board.Zones())

    boardbox = board.ComputeBoundingBox()
    bounds = {
        "x": boardbox.GetX() / 1e6 / 25.4,
        "y": boardbox.GetY() / 1e6 / 25.4,
        "W": boardbox.GetWidth() / 1e6 / 25.4,
        "H": boardbox.GetHeight() / 1e6 / 25.4,
    }
    # print('bounds [inch]:', bounds)

    pctl = pcbnew.PLOT_CONTROLLER(board)

    popt = pctl.GetPlotOptions()
    popt.SetOutputDirectory(plot_dir)
    popt.SetPlotFrameRef(False)
    popt.SetScale(1)
    popt.SetMirror(False)
    popt.SetUseAuxOrigin(False)

    if version <= 6:
        popt.SetExcludeEdgeLayer(False)
        popt.SetDrillMarksType(popt.FULL_DRILL_SHAPE)
    else:
        popt.SetDrillMarksType(pcbnew.DRILL_MARKS_FULL_DRILL_SHAPE)

    plotted_one = False
    for layer in layers:
        pctl.OpenPlotfile(layer, pcbnew.PLOT_FORMAT_PDF, layer)
        try:

            if version <= 6:
                layer_id = board.GetLayerID(layer)
                if layer_id < 0:
                    print(f"layer {layer} not found - skipping")
                else:
                    pctl.SetLayer(layer_id)
                    pctl.PlotLayer()
                    plotted_one = True
            else:
                # Workaround to get the functionality of SetExcludeEdgeLayer(False)
                # https://gitlab.com/kicad/code/kicad/-/issues/13841
                seq = pcbnew.LSEQ()
                seq.push_back(pcbnew.Edge_Cuts)
                layer_id = board.GetLayerID(layer)
                if  layer_id < 0:
                    print(f"layer {layer} not found - skipping")
                else:
                    seq.push_back(board.GetLayerID(layer))
                    pctl.PlotLayers(seq)
                    plotted_one = True

        except Exception:
            print(f"something went wrong plotting {layer}")
        pctl.ClosePlot()

    if not plotted_one:
        print("nothing plotted; aborting")
        raise Exception
    return bounds


if __name__ == "__main__":
    boardName = sys.argv[1]
    plot_dir = sys.argv[2]
    plot_layers(boardName, plot_dir)
