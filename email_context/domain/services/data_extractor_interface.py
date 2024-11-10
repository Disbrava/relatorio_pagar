import pandas as pd
from typing import List, Dict
from abc import ABC, abstractmethod


class DataExtractorInterface(ABC):

    @abstractmethod
    def extract_data_to_report(self, data: Dict[str, pd.DataFrame]) -> [List[pd.DataFrame], ]:
        pass
