import yaml


def load_config(config_path):
    with open(config_path) as f:
        return yaml.safe_load(f)


def print_list_data(file_list, text=""):
    print(f"\n---{text}---")
    if file_list:
        print(f"LEN list: {len(file_list)}")
        # for i in file_list:
        #     print(i)
    else:
        print("Empty list")
