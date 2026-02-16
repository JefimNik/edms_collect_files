import yaml
import os
import pandas as pd
import json


def load_config(config_path):
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def print_list_data(file_list, output_dir=None, text=""):
    print(f"\n---{text}---")
    print(f"LEN list: {len(file_list)}")

    filepath = os.path.join(output_dir, "RawData_paths.txt")

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"\n---{text}---\n")
        f.write(f"LEN list: {len(file_list)}\n")
        for path in file_list:
            f.write(f"          {path}\n")


def config_to_df(config):
    output_dir = config["path_data"]["output_dir"]

    df_config = pd.json_normalize(config).T.reset_index()
    df_config.columns = ["full_key", "value"]

    df_config[["category", "subcategory"]] = (
        df_config["full_key"].str.split(".", n=1, expand=True)
    )

    df_config = df_config[["category", "subcategory", "value"]]

    # 🔥 ВАЖНО — преобразуем list/dict в JSON
    df_config["value"] = df_config["value"].apply(
        lambda x: json.dumps(x, ensure_ascii=False)
        if isinstance(x, (list, dict))
        else x
    )

    return output_dir, df_config
