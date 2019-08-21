import importlib


def resolve_dotted_path(path: str):
    splitted = path.split(".")
    module, attr = ".".join(splitted[:-1]), splitted[-1]
    module = importlib.import_module(module)
    return getattr(module, attr)
