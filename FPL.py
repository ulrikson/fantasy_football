import pandas as pd
import numpy as np


class FPL:
    def __init__(self, json):
        self.json = json

        self.elements_df = pd.DataFrame(json['elements'])
        self.elements_types_df = pd.DataFrame(json['element_types'])
        self.teams_df = pd.DataFrame(json['teams'])

        self.must_be_higher_than_zero = ['value_season', 'form', 'minutes']

    def getPlayerDF(self):
        slim_elements_df = self.elements_df[['second_name', 'team', 'element_type', 'selected_by_percent',
                                             'now_cost', 'minutes', 'transfers_in', 'value_season', 'total_points', 'form']]

        slim_elements_df['position'] = slim_elements_df.element_type.map(
            self.elements_types_df.set_index('id').singular_name)

        slim_elements_df['team'] = slim_elements_df.team.map(
            self.teams_df.set_index('id').name)

        slim_elements_df = self.removeZeroValues(slim_elements_df)

        return slim_elements_df
    
    def removeZeroValues(self, df):
        for column in self.must_be_higher_than_zero:
            df[column] = df[column].astype(float)
            df = df.loc[df[column] > 0]

        return df
