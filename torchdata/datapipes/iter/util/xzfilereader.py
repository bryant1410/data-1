# Copyright (c) Facebook, Inc. and its affiliates.
import os
import lzma
import warnings
from io import BufferedIOBase
from typing import IO, Iterable, Iterator, Optional, Tuple, cast

from torchdata.datapipes.utils.common import validate_pathname_binary_tuple
from torch.utils.data import IterDataPipe, functional_datapipe

@functional_datapipe('read_from_xz')
class XzFileReaderIterDataPipe(IterDataPipe[Tuple[str, BufferedIOBase]]):
    r"""

    Iterable datapipe to uncompress xz (lzma) binary streams from input iterable which contains tuples of
    pathname and xz binary stream, yields pathname and extracted binary stream in a tuple.
    args:
        datapipe: Iterable datapipe that provides pathname and xz binary stream in tuples
        length: a nominal length of the datapipe

    Note:
        The opened file handles will be closed automatically if the default DecoderDataPipe
        is attached. Otherwise, user should be responsible to close file handles explicitly
        or let Python's GC close them periodly.
    """
    def __init__(
            self,
            datapipe : Iterable[Tuple[str, BufferedIOBase]],
            length : int = -1):
        super().__init__()
        self.datapipe : Iterable[Tuple[str, BufferedIOBase]] = datapipe
        self.length : int = length


    def __iter__(self) -> Iterator[Tuple[str, BufferedIOBase]]:
        if not isinstance(self.datapipe, Iterable):
            raise TypeError("datapipe must be Iterable type but got {}".format(type(self.datapipe)))
        for data in self.datapipe:
            validate_pathname_binary_tuple(data)
            pathname, data_stream = data
            try:
                extracted_fobj = lzma.open(data_stream, "rb")
                new_pathname = pathname.rstrip(".xz")
                yield (new_pathname, cast(BufferedIOBase, extracted_fobj))
            except Exception as e:
                warnings.warn(
                    "Unable to extract files from corrupted xz/lzma stream {} due to: {}, abort!".format(pathname, e))
                raise e


    def __len__(self):
        if self.length == -1:
            raise TypeError("{} instance doesn't have valid length".format(type(self).__name__))
        return self.length
