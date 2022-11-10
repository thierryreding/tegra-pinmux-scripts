#!/usr/bin/env python3

# Copyright (c) 2022, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import argparse
import os
import os.path
import sys
import textwrap

parser = argparse.ArgumentParser(description = 'Create a kernel I/O pad driver from an SoC ' +
                                               'config file')
parser.add_argument('soc', help = 'SoC to process')
parser.add_argument('--verbose', action = 'store_true')
args = parser.parse_args()

script_dir = os.path.dirname(os.path.abspath(__file__))
configs_dir = os.path.join(script_dir, 'configs')

filename = os.path.join(configs_dir, args.soc + '-iopad.soc')
values = {}

socvars = {
        'soc': args.soc
    }

with open(filename, 'r') as fobj:
    code = compile(fobj.read(), filename, 'exec')
    exec(code, globals(), values)

print('''\
#define TEGRA_IO_PAD(_id, _dpd, _request, _status, _voltage, _name)\t\\
\t((struct tegra_io_pad_soc) {\t\t\t\t\t\\
\t\t.id\t\t= (_id),\t\t\t\t\\
\t\t.dpd\t\t= (_dpd),\t\t\t\t\\
\t\t.request\t= (_request),\t\t\t\t\\
\t\t.status\t\t= (_status),\t\t\t\t\\
\t\t.voltage\t= (_voltage),\t\t\t\t\\
\t\t.name\t\t= (_name),\t\t\t\t\\
\t})
''')

print('''\
#define TEGRA_IO_PIN_DESC(_id, _name)\t\\
\t((struct pinctrl_pin_desc) {\t\\
\t\t.number\t= (_id),\t\\
\t\t.name\t= (_name),\t\\
\t})
''')

print('static const struct tegra_io_pad_soc %(soc)s_io_pads[] = {' % socvars)

if args.verbose:
    prefix = '\t'

for name, dpd, request, status, voltage in values['iopads']:
    pad_id = 'TEGRA_IO_PAD_%s' % name.upper().replace('-', '_')

    if dpd is not None:
        dpd = '%u' % dpd
    else:
        dpd = 'UINT_MAX'

    if request is not None:
        request = '%#x' % request
    else:
        request = 'UINT_MAX'

    if status is not None:
        status = '%#x' % status
    else:
        status = 'UINT_MAX'

    if voltage is not None:
        voltage = '%u' % voltage
    else:
        voltage = 'UINT_MAX'

    if args.verbose:
        print('%s{' % prefix)
        print('\t\t.id = %s,' % pad_id)
        print('\t\t.dpd = %s,' % dpd)
        print('\t\t.request = %s,' % request)
        print('\t\t.status = %s,' % status)
        print('\t\t.voltage = %s,' % voltage)
        print('\t\t.name = "%s",' % name)
        print('\t}', end = '')

        prefix = ', '
    else:
        print('\tTEGRA_IO_PAD(%s, %s, %s, %s, %s, "%s"),' % (pad_id, dpd, request,
                                                             status, voltage, name))

if args.verbose:
    print()

print('};')
print()
print('static const struct pinctrl_pin_desc %(soc)s_pin_descs[] = {' % socvars)

if args.verbose:
    prefix = '\t'

for name, dpd, request, status, voltage in values['iopads']:
    pad_id = 'TEGRA_IO_PAD_%s' % name.upper().replace('-', '_')

    if args.verbose:
        print('%s{' % prefix)
        print('\t\t.number = %s,' % pad_id)
        print('\t\t.name = "%s",' % name)
        print('\t}', end = '')

        prefix = ', '
    else:
        print('\tTEGRA_IO_PIN_DESC(%s, "%s"),' % (pad_id, name))


if args.verbose:
    print()

print('};')
