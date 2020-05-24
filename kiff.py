#!/usr/bin/env python
# tested on Python 2 & Python 3
'''
Kiff, the Kicad Diff!

Graphically compare layout changes between two git versions of a PCB.

If `-c` is not given, compares the local working copy against the latest
commited version from git. This is useful to verify board changes before
committing them.

If a git commit-id is given in `-c`, will compare the local version
against this commit. This is useful to compare changes between 2 commits.

A useful shortcut for the commit-id is `HEAD~1`, which means the previous one.

Elements which have been added in the local version are colored green,
removed ones red.
Note that this may look inverted for features on copper fills.
'''
import argparse
from PIL import Image
from numpy import array, zeros, uint8, sum
from subprocess import call, check_output
from io import BytesIO
from os.path import splitext, join
from os import mkdir
from shutil import rmtree
from plot_layers import plot_layers


def img_diff(i1, i2, doInvert=True):
    '''
    i1, i2: PIL Image objects of same size to compare
    doInvert: set true when input is black on white background
    returns: PIL Image of the diff
    '''
    a0 = array(i1)
    a1 = array(i2)
    if doInvert:
        a0 = ~a0
        a1 = ~a1
    a_out = zeros((a0.shape[0], a0.shape[1], 3), dtype=uint8)

    # bit-wise logic applied to all uint8 pixel values
    common = a0 & a1
    diff1 = a1 & ~common
    diff2 = a0 & ~common

    # assign results to color channels
    a_out[:, :, 0] = common * 0.2 + diff1 * 0.8  # Red
    a_out[:, :, 1] = common * 0.2 + diff2 * 0.8  # Green
    a_out[:, :, 2] = common * 0.2                # Blue

    # how many pixels changed in the whole image: 1.0 = all pixels changed
    added = float(sum(diff1)) / sum(a0)  # python2 loves integers too much!
    removed = float(sum(diff2)) / sum(a0)

    return Image.fromarray(a_out), added, removed


def load_pdf(fName, x=4.7, y=2.6, W=7.3, H=6.0, r=600):
    '''
    fName: .pdf file to load
    x, y, W, H: crop window [inch]
    r: resolution [dpi]
    returns: PIL Image
    '''
    ppm_str = check_output([
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
    tmp = check_output(['git', 'describe', '--dirty', '--always'])
    return tmp.decode('ascii').strip()


def co(cmds):
    ''' run and print cmds, raises exception if command returns != 0 '''
    print('$ ' + ' '.join(cmds))
    check_output(cmds)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'kicad_pcb',
        help='the `.kicad_pcb` file to DIFF'
    )
    parser.add_argument(
        '-c', '--commit',
        default='HEAD',
        help='git commit-id to compare current version against. Default: HEAD'
    )
    parser.add_argument(
        '-l', '--layers',
        default=0,
        type=int,
        help='Number of inner layers (InX.Cu) to plot. Default: 0'
    )
    parser.add_argument(
        '-r', '--resolution',
        default=400,
        type=int,
        help='Plotting resolution in [dpi]. Default: 400'
    )
    parser.add_argument(
        '-k', '--keep',
        action='store_true',
        help='Don`t delete temporary .pdf layer plots'
    )
    args = parser.parse_args()

    layers = ['F.Cu', 'B.Cu', 'F.SilkS', 'B.SilkS']
    layers += ['In{}.Cu'.format(i + 1) for i in range(args.layers)]
    print('layers: ' + ' '.join(layers))

    # Check for local (un-commited) changes
    do_stash = call(['git', 'diff-index', '--quiet', 'HEAD', '--']) > 0
    if not do_stash and args.commit == 'HEAD':
        print('No local changes, nothing to compare. Try -c <commit-id>')
        return -1

    # output directory name is derived from `git describe`
    try:
        git1_name = desc()
    except Exception:
        # this will happen if user isn't in a git repo
        print("No git description, can't continue")
        exit(1)

    # Do a .pdf plot of the current version
    dir1 = 'plot_' + git1_name
    print('> ' + dir1)
    bounds1 = plot_layers(args.kicad_pcb, dir1, layers)
    if bounds1 is None:
        exit(1)

    # Stash local changes if needed
    if do_stash:
        co(['git', 'stash'])

    # checkout specified git version (default: HEAD) ...
    if args.commit != 'HEAD':
        co(['git', 'checkout', args.commit])

    # ... and do a .pdf plot of it
    dir2 = 'plot_' + desc()
    print('> ' + dir2)
    bounds2 = plot_layers(args.kicad_pcb, dir2, layers)
    if bounds2 is None:
        exit(1)

    # Switch back to current version
    if args.commit != 'HEAD':
        co(['git', 'checkout', '-'])

    # Restore local changes
    if do_stash:
        co(['git', 'stash', 'pop'])

    # Generate plots into `diffs` directory
    try:
        mkdir('diffs')
    except OSError:
        print('diffs directory already exists')

    # Create a .png diff for each layer
    diff_cntr = 0
    for ll in layers:
        pdf_name = splitext(args.kicad_pcb)[0]
        pdf_name += '-' + ll.replace('.', '_') + '.pdf'
        out_file = 'diffs/' + ll + '.png'

        i1 = load_pdf(join(dir1, pdf_name), r=args.resolution, **bounds1)
        i2 = load_pdf(join(dir2, pdf_name), r=args.resolution, **bounds1)
        i_out, added, removed = img_diff(i1, i2)
        i_out.save(out_file)

        print('> {:18s} (+{:.6f}, -{:.6f})'.format(out_file, added, removed))
        diff_cntr += added + removed

    if diff_cntr == 0:
        print("No visual changes detected")

    if not args.keep:
        print('Removing temporary directories')
        rmtree(dir1)
        rmtree(dir2)


if __name__ == '__main__':
    main()
