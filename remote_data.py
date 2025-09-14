#

from influxdb_client import InfluxDBClient
from cred import *
from text_on_template_to_c_program import run_epd_with_text

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
    items = []
    for field, vals in values_by_field.items():
        # sort by time ascending
        vals.sort(key=lambda x: x[0])
        # take last 3
        last_three = vals[-3:]
        last_time, last_value = last_three[-1]
        avg = sum(v for _, v in last_three) / len(last_three)
        # print(f"Field: {field}")
        # print(f"  Last: {last_time} = {last_value}")
        # print(f"  Avg(last {len(last_three)}): {avg:.3f}")
        items.append({
            "field": field,
            "timestamp": last_time,
            "value": last_value,
            "avg_last_3": round(avg, 2)
        })
    return items

def sensor__get_remote_data():

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
    return data_by_device

def sensor__items_to_textitems(data_by_device):
    items = summarize_device(data_by_device["0"])
    # print(items)
    text_items = []
    # Field: air_quality
    # Last: 2025-09-06 16:44:16+00:00 = 93.274
    # Avg(last 3): 93.308
    # Field: battery_voltage
    # Last: 2025-09-06 16:44:16+00:00 = 4.212
    # Avg(last 3): 4.220
    inner__y_distance = 20
    outer__y_distance = 90
    from__y = 200
    for i in range(0, len(items)):
        item = items[i]
        # {
        #     "field": field,
        #     "timestamp": last_time,
        #     "value": last_value,
        #     "avg_last_3": round(avg, 2)
        # }
        text_items.append({
            "text": item["field"],
            "box": [40, from__y + i * outer__y_distance, 999, 999],
            "size": 20,
            "color": "red",
            "style": "bold",
        })
        text_items.append({
            "text": "Value:" + str(item["value"]),
            "box": [80, from__y + i * outer__y_distance + inner__y_distance, 999, 999],
            "size": 16,
            "color": "black",
            "style": "bold",
        })
        text_items.append({
            "text": "Timestamp: " + item["timestamp"].strftime("%H:%M:%S %d:%m:%Y"),
            "box": [80, from__y + i * outer__y_distance + 2 * inner__y_distance, 999, 999],
            "size": 16,
            "color": "black",
            "style": "bold",
        })
        text_items.append({
            "text": "Average of last 3: " + str(item["avg_last_3"]),
            "box": [80, from__y + i * outer__y_distance + 3 * inner__y_distance, 999, 999],
            "size": 16,
            "color": "black",
            "style": "bold",
        })
        if i == 3:
            break
    return text_items

if __name__ == "__main__":
    data_by_device = sensor__get_remote_data()
    text_items = sensor__items_to_textitems(data_by_device)
    # # Print results grouped per device
    # tryit = False
    # if tryit:
    #     for box_id, records in data_by_device.items():
    #         print("=" * 40)
    #         print(f"Device: {box_id}")
    #         print("=" * 40)
    #         for r in records:
    #             print(f"{r.get_time()} | {r.get_field()} = {r.get_value()}")
    # else:
    #     items = summarize_device(data_by_device["0"])
    #     print(items)
    #     text_items = []
    #     # Field: air_quality
    #     # Last: 2025-09-06 16:44:16+00:00 = 93.274
    #     # Avg(last 3): 93.308
    #     # Field: battery_voltage
    #     # Last: 2025-09-06 16:44:16+00:00 = 4.212
    #     # Avg(last 3): 4.220
    #     inner__y_distance = 20
    #     outer__y_distance = 90
    #     from__y = 200
    #     for i in range(0, len(items)):
    #         item = items[i]
    #         # {
    #         #     "field": field,
    #         #     "timestamp": last_time,
    #         #     "value": last_value,
    #         #     "avg_last_3": round(avg, 2)
    #         # }
    #         text_items.append({
    #             "text": item["field"],
    #             "box": [40, from__y + i * outer__y_distance, 999, 999],
    #             "size": 20,
    #             "color": "red",
    #             "style": "bold",
    #         })
    #         text_items.append({
    #             "text": "Measurement at: " + str(item["timestamp"]),
    #             "box": [80, from__y + i * outer__y_distance + inner__y_distance, 999, 999],
    #             "size": 16,
    #             "color": "black",
    #             "style": "bold",
    #         })
    #         text_items.append({
    #             "text": "Value:" + str(item["value"]),
    #             "box": [80, from__y + i * outer__y_distance + 2 * inner__y_distance, 999, 999],
    #             "size": 16,
    #             "color": "black",
    #             "style": "bold",
    #         })
    #         text_items.append({
    #             "text": "Average of last 3 earlier measurements: " + str(item["avg_last_3"]),
    #             "box": [80, from__y + i * outer__y_distance + 3 * inner__y_distance, 999, 999],
    #             "size": 16,
    #             "color": "black",
    #             "style": "bold",
    #         })
    #         if i == 3:
    #             break
    #     print(text_items)
    run_epd_with_text(items=text_items, black_bmp_name="kiezbox_sensor_black_white.bmp", ry_bmp_name="kiezbox_sensor_red_white.bmp")