import pandas as pd
from typing import List
from abc import ABC, abstractmethod


class DataExtractorInterface(ABC):

    @abstractmethod
    def extract_data_to_report(self) -> List[pd.DataFrame]:
        pass
