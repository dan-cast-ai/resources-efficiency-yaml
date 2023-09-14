from constants import GB_BYTES


def convert_gb_to_bytes(gb):
    bytes_per_gb = GB_BYTES  # 1 GB = 1,073,741,824 bytes
    gb = float(gb)  # Convert to float
    # print(gb)
    return int(gb * bytes_per_gb)
