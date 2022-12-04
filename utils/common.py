import hashlib


def create_int_hash_from_df_row(row):
    """Convert all columns of a row into string, concatenate and return 8 digit int
    representation of MD5 hash.
    """
    row_string = "-".join(row.values.astype(str))
    return int(hashlib.md5(row_string.encode("utf-16")).hexdigest(), 16) % 10**8
