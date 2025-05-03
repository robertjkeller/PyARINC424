[![Tests](https://github.com/robertjkeller/PyARINC424/actions/workflows/python-tests.yml/badge.svg)](https://github.com/robertjkeller/PyARINC424/actions/workflows/python-tests.yml) ![Coverage Status](./assets/badges/coverage-badge.svg?dummy=8484744)

# PyARINC424

## About

PyARINC424 is a tool that parses an [ARINC-424](https://en.wikipedia.org/wiki/ARINC_424) formatted data file into a PostreSQL database. PyARINC424 supports the tables/records that are currently output in [FAA CIFP](https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/cifp/download/):
- Airports and heliports (PA and HA)
- Runways (PG)
- VHF Navaids (D)
- NDB Navaids (DB)
- Terminal Navaids (PN)
- Localizer and Glide Slope Records (PI)
- Path Point Records, Primary and Continuation (PP)
- MSA Records (PS and HS)
- Enroute Waypoints (EA)
- Terminal Waypoints (PC and HC)
- SIDs (PD)
- STARs (PE)
- Approaches, including Level of Service continuation records (PF and HF)
- Airways (ER)
- Class B, C, and D Airspace (UC)
- Special Use Airspace, Primary and Continuation (UR)
- Grid MORA (AS)

## Config File
By default, the program looks for a `config.ini` file in the application `src` directory.
You can specify a different config path by passing it as an argument:
```sh
python main.py /path/to/my_config.ini
```

The config can be set up for *either* PostgreSQL or SQLite.

A PostgreSQL configuration file should contain the following:
```
[postgres]
dbname =    # your database name (must already exist)
user =      # your postgres username
password =  # your postgres password
host =      # your host, e.g. localhost
port =      # your postgres port, e.g. 5432

[cifp_file]
file_loc =  # your ARINC file location
```

A SQLite configuration file should contain the following:
```
[sqlite]
dbname =    # your output SQLite db file name

[cifp_file]
file_loc =  # your ARINC file location
```
