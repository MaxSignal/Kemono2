from pathlib import Path


class CONSTANTS:
    PROJECT_PATH = Path(__file__, '..', '..').resolve()
    TEST_PATH = PROJECT_PATH.joinpath('test')
    CLIENT_FILES_FOLDER = PROJECT_PATH.joinpath('dist')
    TEMPLATES_FOLDER = CLIENT_FILES_FOLDER.joinpath('pages')
