from pathlib import Path

project_path = Path(__file__, '..', '..').resolve()
test_path = project_path.joinpath('test')
client_files_folder = project_path.joinpath('dist')
templates_folder = client_files_folder.joinpath('pages')


class CONSTANTS:
    PROJECT_PATH = project_path
    TEST_PATH = test_path
    CLIENT_FILES_FOLDER = client_files_folder
    TEMPLATES_FOLDER = templates_folder
