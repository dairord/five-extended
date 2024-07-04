from pathlib import Path
import shutil

base_dir = Path(__file__).parent.parent

def save_current_project(project_name):
    standard_path = base_dir / "projects" / project_name
    move_to_folder(standard_path)


def save_project_in(custom_path, project_name):
    custom_project_path = custom_path / project_name
    move_to_folder(custom_project_path)


def move_file(file_path, new_folder_path, new_name):
    if file_path.is_file() and new_folder_path.is_dir():
        shutil.copy2(str(file_path), str(new_folder_path / new_name))
        return True
    return False



def move_to_folder(save_folder_path):
    tmp_path = base_dir / "out"

    save_folder_path.mkdir(parents=True, exist_ok=True)

    for path in tmp_path.iterdir():
        if path.is_file():
            new_path = save_folder_path / path.name
            shutil.copy2(str(path), str(new_path))
    clean_out_folder()



def clean_out_folder():
    out_path = base_dir / "out"

    for path in out_path.iterdir():
        if path.is_file():
            path.unlink()

def exists_project_folder(project_name):
    path = base_dir / "projects" / project_name

    return path.is_dir()