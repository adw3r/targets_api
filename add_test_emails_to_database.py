from pathlib import Path

from config import TARGETS_FOLDER


def get_database(path: Path | str):
    with open(path, encoding='latin-1') as f:
        return f.read().split('\n')


def save_database(path: Path | str, list_to_save: list):
    with open(path, 'w', encoding='latin-1') as f:
        f.write('\n'.join(list_to_save))


def main():
    files = (
        'fkasn23.csv',
        'pobcasn23.csv',
    )
    for file in files:
        print(file)
        file_name = file.removesuffix('.csv')
        original_list = get_database(Path(TARGETS_FOLDER, file))
        step = 500
        cc = step
        c = 1
        while cc < len(original_list):
            original_list.insert(cc, f'radarodionova71+{file_name}{c}@gmail.com')
            original_list.insert(cc, f'softumwork+{file_name}{c}@gmail.com')
            cc += step
            c += 1
        save_database(Path(TARGETS_FOLDER, f'test_{file_name}.csv'), original_list)


if __name__ == '__main__':
    main()
