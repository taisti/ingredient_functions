from pathlib import Path
import pandas as pd


class DiskStorage:
    def __init__(self, session_id: str, data_path: Path = Path('./')) -> None:
        self._session_id = session_id
        self._store = pd.HDFStore(path=(data_path / session_id).with_suffix('.h5'), mode='a')

    def store(self, data: pd.DataFrame, *, group: str) -> None:
        self._store.append(key=group, value=data, min_itemsize=512)
        self._store.flush(fsync=True)  # TODO

    def get(self, *, group: str) -> pd.DataFrame:
        return self._store.select(key=group)

    def __len__(self, group: str) -> int:
        try:
            return len(self.get(group=group))
        except KeyError:
            return 0

    def __del__(self):
        try:
            self._store.close()
        except (AttributeError, NameError):
            pass
