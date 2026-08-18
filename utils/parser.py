from getgauge.python import Table
from datetime import datetime
from typing import Any, Dict

def table_to_dict(table:Table) -> Dict[str, Any]:
    """Gauge <table> 参数转 dict。兼容 Table 对象(.rows/.cells)和原始 list-of-tuples。"""
    r = {}
    headers = table.headers
    row = table.rows[0]
    for index, key in enumerate(headers):
        row_info = row[index]
        r[key] = row_info
    return r


def gen_date_number() ->str:
    return datetime.now().strftime("%Y%m%d%H%M%S")



if __name__ == "__main__":
    print(gen_date_number())