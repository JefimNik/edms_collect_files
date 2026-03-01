import yaml
import os


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
