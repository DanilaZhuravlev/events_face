import pathlib
import subprocess

import toml


def update_pyproject_toml():
    """Обновляет pyproject.toml с зависимостями из виртуального окружения."""
    # Получаем список установленных пакетов
    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
    packages = result.stdout.strip().split("\n")

    # Форматируем зависимости для pyproject.toml
    dependencies = []
    for package in packages:
        if "==" in package:
            name, version = package.split("==")
            dependencies.append(f"{name}=={version}")
        else:
            dependencies.append(package)

    # Читаем pyproject.toml
    pyproject_path = pathlib.Path("pyproject.toml")
    pyproject_data = toml.loads(pyproject_path.read_text())

    # Добавляем зависимости
    if "dependencies" not in pyproject_data["project"]:
        pyproject_data["project"]["dependencies"] = []
    pyproject_data["project"]["dependencies"].extend(dependencies)

    # Записываем изменения в pyproject.toml
    pyproject_path.write_text(toml.dumps(pyproject_data))


if __name__ == "__main__":
    update_pyproject_toml()
