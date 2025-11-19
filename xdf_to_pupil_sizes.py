import pyxdf
import json
import numpy as np
import os
from typing import List

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        
        if isinstance(obj, np.integer):
            return int(obj)
            
        if isinstance(obj, np.floating):
            return float(obj)
            
        return json.JSONEncoder.default(self, obj)


class XdfToJsonConverter:

    def __init__(self, xdf_path: str):
        self.xdf_path = xdf_path
        self.json_data = {}

    def convert_to_json(self):
        xdf_path = self.xdf_path
        print(f"Input File: {os.path.basename(xdf_path)}", file=sys.stderr)

        try:
            streams, header = pyxdf.load_xdf(xdf_path)
        except Exception as e:
            print(f"Error loading XDF file: {e}", file=sys.stderr)
            raise

        self.json_data = {
            "xdf_header": header,
            "streams": []
        }

        for i, stream in enumerate(streams):
            stream_name = stream.get('info', {}).get('name', ['UNKNOWN'])[0]
            sample_count = 0
            if 'time_series' in stream and stream['time_series'] is not None:
                sample_count = len(stream['time_series'])
            self.json_data["streams"].append(stream)

        print(f"Loaded data successfully", file=sys.stderr)

    def extract_pupil_size_list(self):
        for stream in self.json_data.get('streams', []):
            stream_name = stream.get('info', {}).get('name', [''])[0]

            if 'pupil' in stream_name.lower():
                ts = stream.get('time_series')
                if ts is None or len(ts) == 0:
                    continue

                # Case 1: Flat list (First item is a number)
                if isinstance(ts[0], (int, float, complex)):
                    return ts

                # Case 2: 2D List (List of Lists)
                for col in zip(*ts):
                    if any(val != -1 for val in col):
                        return list(col)
        return []

    def get_pupil_data(self) -> List[float]:
        self.convert_to_json()
        return self.extract_pupil_size_list()


def run(path: str):
    converter = XdfToJsonConverter(path)
    return converter.get_pupil_data()


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Missing path to xdf file", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]

    try:
        result = run(path)
        print(json.dumps(result, cls=NumpyEncoder))
    except Exception as e:
        print(f"Error processing XDF: {e}", file=sys.stderr)
        sys.exit(1)
