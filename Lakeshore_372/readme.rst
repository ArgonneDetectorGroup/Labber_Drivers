Lakeshore 372 Driver
====================
This driver supports multiple scanner options.
To select the scanner, change the "scanner_type" value in
`Lakeshore_372.ini.yml` to the appropriate scanner model.
Then, open a terminal and rebuild the driver .ini file with `yasha`.
Note: on Windows, use the anaconda terminal so the env vars get set correctly.::

  yasha -e yasha_extensions.py Lakeshore_372.ini.j2

This should result in a newly built Lakeshore_372.ini file!

Don't edit the .ini file directly. Instead, edit the .ini.j2 template file
and then rerun the above command to rebuild the driver.

If you don't have yasha installed, you can get it via::

  pip install yasha


yasha uses `jinja2` under the hood, so you can use the documentation
for that package to make edits to the template file.
