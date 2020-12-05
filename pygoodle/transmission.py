"""pygoodle transmission utilities

.. codeauthor:: Joe DeCapo <joe@polka.cat>

"""

from collections import deque
from typing import List

from .ssh import SecureShell


class Torrent(object):

    def __init__(self, **kwargs):
        self.id = kwargs['ID']
        self.done = kwargs['Done']
        self.have = kwargs['Have']
        self.eta = kwargs['ETA']
        self.up = kwargs['Up']
        self.down = kwargs['Down']
        self.ratio = kwargs['Ratio']
        self.status = kwargs['Status']
        self.name = kwargs['Name']


class Transmission(object):

    def __init__(self):
        self._ssh = SecureShell()
        # self._torrents: Optional[List[Torrent]] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self) -> None:
        self._ssh.close()

    @property
    def torrents(self) -> List[Torrent]:
        result = self._ssh.run_command('transmission-remote --list')
        rows = deque(result.stdout.split('\n'))
        headers = rows.popleft().split()
        rows.pop()
        torrents = []
        for row in rows:
            kwargs = {h: v for h in headers for v in row}
            torrent = Torrent(**kwargs)
            torrents.append(torrent)
        return torrents
