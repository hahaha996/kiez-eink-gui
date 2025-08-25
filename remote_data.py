#

from influxdb_client import InfluxDBClient
from cred import *


client = InfluxDBClient(url=DB_URL, token=DB_TOKEN, org=DB_ORG)


query_api = client.query_api()

def summarize_device(records):
    """
    records: list of influxdb_client.client.flux_table.FluxRecord
             belonging to a single device (e.g. data_by_device["0"])
    Prints, for each field, the last measurement and the average of the last 3.
    """
    from collections import defaultdict, deque

    # group values by field
    values_by_field = defaultdict(list)
    for r in records:
        values_by_field[r.get_field()].append((r.get_time(), r.get_value()))

    # process each field
    for field, vals in values_by_field.items():
        # sort by time ascending
        vals.sort(key=lambda x: x[0])
        # take last 3
        last_three = vals[-3:]
        last_time, last_value = last_three[-1]
        avg = sum(v for _, v in last_three) / len(last_three)
        print(f"Field: {field}")
        print(f"  Last: {last_time} = {last_value}")
        print(f"  Avg(last {len(last_three)}): {avg:.3f}")


flux = '''
from(bucket: "kiezbox-test")
  |> range(start: -10h)
  |> filter(fn: (r) => r["_measurement"] == "sensor_values")
  |> filter(fn: (r) => r["_field"] == "humid_main" or r["_field"] == "part_pm10" or r["_field"] == "part_pm25" or r["_field"] == "temp_main")
'''

flux = '''
from(bucket: "kiezbox-test")
  |> range(start: -30m)   // or your v.timeRangeStart/Stop
  |> filter(fn: (r) => r["_measurement"] == "sensor_values" or r["_measurement"] == "core_values")
  |> filter(fn: (r) => r["_field"] == "humid_main"
                    or r["_field"] == "part_pm10"
                    or r["_field"] == "part_pm25"
                    or r["_field"] == "temp_main"
                    or r["_field"] == "battery_voltage"
                    or r["_field"] == "air_quality"
                    or r["_field"] == "pressure")
'''

tables = query_api.query(flux)

# Group by device (box_id)
data_by_device = {}
for table in tables:
    for record in table.records:
        box_id = record.values.get("box_id", "UNKNOWN")
        data_by_device.setdefault(box_id, []).append(record)

# Print results grouped per device
tryit = False
if tryit:
    for box_id, records in data_by_device.items():
        print("=" * 40)
        print(f"Device: {box_id}")
        print("=" * 40)
        for r in records:
            print(f"{r.get_time()} | {r.get_field()} = {r.get_value()}")
else:
    summarize_device(data_by_device["0"])
