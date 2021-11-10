# Functions used in jsonprocessor.py.
import pandas as pd

def codeConverter(value):
        """Converts province or territory 2-letter alpha code to corresponding SGC code."""
        d = pd.read_csv("input/prov-terr.csv").set_index("Alpha_codes")['SGC_code'].to_dict()
        return d[value]

def _isForceValue(self, value):
        """Returns True if value contains the prefix 'force:'."""
        self.FORCE_REGEXP = re.compile(r'force:.*', re.UNICODE)
        return bool(self.FORCE_REGEXP.match(value))
