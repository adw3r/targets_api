from app.targets import utils


def test_add_targets_to_db():
    lang = 'eng'
    source_name = 'dzusuk'
    filename = 'dz_usuk.txt'
    utils.add_targets_to_db(source_name=source_name, lang=lang, input_file_name=filename)
