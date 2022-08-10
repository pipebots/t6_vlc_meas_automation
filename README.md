```
 __________.__             ___.     |__|  __
 \______   \__|_____   ____\_ |__   _||__/  |_  ______ (C) George Jackson-Mills 2020
  |     ___/  \____ \_/ __ \| __ \ /  _ \   __\/  ___/
  |    |   |  |  |_> >  ___/| \_\ (  O_O )  |  \___ \
  |____|   |__|   __/ \___  >___  /\____/|__| /____  >
              |__|        \/    \/                 \/
```

# Visible Light Communication (VLC) Test and Measurement Automation

## Overview

Python scripts used for automating VLC experiments and measurements at 2.61B at Leeds. The scripts connect to and control various instruments through either VISA commands over Ethernet/GPIB; or through raw byte strings sent over UDP in the case of a particular power supply unit.

The files in the `instruments` subfolder are Viktor's attempt at coming up with an object-oriented representation of the different instruments. However, the scripts in the main folder should be preferred as they have been tested more extensively.

## Requirements

Only requirement for a third-party library is `pyvisa`. However, you would also need to have installed either Keysight's or National Instruments' VISA libraries, which `pyvisa` wraps.

## Contributing

Contributions are more than welcome and are in fact actively sought! Please contact either Viktor at [v.doychinov@bradford.ac.uk](mailto:v.doychinov@bradford.ac.uk) or Tim Amsdon at [t.j.amsdon@leeds.ac.uk](mailto:t.j.amsdon@leeds.ac.uk).

## Acknowledgements

This work is supported by the UK's Engineering and Physical Sciences Research Council (EPSRC) Programme Grant EP/S016813/1
