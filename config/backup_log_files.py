#!/usr/bin/env python3
#-*-encoding:utf-8*-

from zipfile import ZipFile, ZIP_DEFLATED
import os, sys

srcdir = sys.argv[1]
dstdir = sys.argv[2]

zip_filename = None
z = None
for d, sd, files in os.walk(srcdir):
    for f in files:
        if z is None:
            l = f.replace("__", "_").split("_")
            zip_filename = "_".join(l[:-8] + l[-6:-3] + [''] + l[-3:-1]) + ".zip"
            zip_path = dstdir + "/" + zip_filename
            z = ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED, compresslevel=1)
        z.write(d + f)
        os.remove(d + f)

if z is not None:
    z.close()
