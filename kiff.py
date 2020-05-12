#!/usr/bin/env python2
'''
Kiff, the Kicad Diff!
'''
# Sorry, pcbnew works for me only with python2 :(
import argparse
from PIL import Image
from numpy import array, zeros, uint8
import subprocess
from io import BytesIO
from os.path import splitext, join
from os import mkdir, system
from shutil import rmtree
from plot_layers import plot_layers


def img_diff(i1, i2, doInvert=True):
    ''' doInvert: set true whe input is black on white background '''
    a0 = array(i1)
    a1 = array(i2)
    if doInvert:
        a0 = ~a0
        a1 = ~a1
    a_out = zeros((a0.shape[0], a0.shape[1], 3), dtype=uint8)

    # Black background (looks nicer!)
    common = a0 & a1
    diff1 = a1 & ~common
    diff2 = a0 & ~common

    a_out[:, :, 0] = common * 0.2 + diff1 * 0.8
    a_out[:, :, 1] = common * 0.2 + diff2 * 0.8
    a_out[:, :, 2] = common * 0.2

    # White background (simpler!)
    # a_out[:, :, 0] = a0
    # a_out[:, :, 1] = a1
    # a_out[:, :, 2] = a0 & a1

    return Image.fromarray(a_out)


def load_svg(fName):
    ''' not used '''
    png_str = subprocess.check_output(['rsvg-convert', '-b', 'white', fName])
    return Image.open(BytesIO(png_str)).convert('L')


def load_pdf(fName, x=4.7, y=2.6, W=7.3, H=6.0, r=600):
    '''
    x, y, W, H: crop window [inch]
    r: resolution [dpi]
    '''
    ppm_str = subprocess.check_output([
        'pdftoppm',
        '-r', str(int(r)),
        '-x', str(int(x * r)),
        '-y', str(int(y * r)),
        '-W', str(int(W * r)),
        '-H', str(int(H * r)),
        fName
    ])
    return Image.open(BytesIO(ppm_str)).convert('L')


def desc():
    ''' the git describe string '''
    return subprocess.check_output(['git', 'describe']).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'kicad_pcb',
        help='the `.kicad_pcb` file to DIFF'
    )
    parser.add_argument(
        '-c', '--commit',
        default='HEAD~1',
        help='git commit-id to compare current version against'
    )
    parser.add_argument(
        '-l', '--layers',
        default=0,
        type=int,
        help='Number of inner layers (InX.Cu) to plot'
    )
    args = parser.parse_args()

    layers = ['F.Cu', 'B.Cu', 'F.SilkS', 'B.SilkS']
    layers += ['In{}.Cu'.format(i + 1) for i in range(args.layers)]
    print(layers)

    # Do a plot of the current version
    # output directory name is derived from `git describe`
    dir1 = 'plot_' + desc()
    print('Plot into ' + dir1)
    bounds1 = plot_layers(args.kicad_pcb, dir1, layers)

    # Checkout older version and plot it
    system('git checkout {}'.format(args.commit))
    dir2 = 'plot_' + desc()
    print('Plot into ' + dir2)
    bounds2 = plot_layers(args.kicad_pcb, dir2, layers)

    # Switch back to current version
    system('git checkout -')

    try:
        mkdir('diffs')
    except OSError:
        pass

    # Create a .png diff for each layer
    for ll in layers:
        pdf_name = splitext(args.kicad_pcb)[0]
        pdf_name += '-' + ll.replace('.', '_') + '.pdf'

        out_file = 'diffs/' + ll + '.png'
        print(out_file)

        i1 = load_pdf(join(dir1, pdf_name), r=400, **bounds1)
        i2 = load_pdf(join(dir2, pdf_name), r=400, **bounds1)
        i_out = img_diff(i1, i2)
        i_out.save(out_file)

    rmtree(dir1)
    rmtree(dir2)


if __name__ == '__main__':
    main()
