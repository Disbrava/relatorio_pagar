import pandas as pd
from uuid import UUID
from typing import List, Dict, Union
from abc import ABC, abstractmethod


class DataExtractorServiceInterface(ABC):

    @abstractmethod
    def extract_data_to_report(self, data: Dict[str, pd.DataFrame]) -> Union[UUID, str]:
        pass
