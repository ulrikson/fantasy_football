import pandas as pd
import numpy as np


class Fantasy:
    def __init__(self, json, unwanted_teams, higher_than_zero):
        self.json = json

        self.elements_df = pd.DataFrame(json['elements'])
        self.elements_types_df = pd.DataFrame(json['element_types'])
        self.teams_df = pd.DataFrame(json['teams'])

        self.unwanted_teams = unwanted_teams
        self.higher_than_zero = higher_than_zero

    def getPlayerDf(self):
        df = self.elements_df[['second_name', 'team', 'element_type',
                               'now_cost', 'minutes', 'value_season', 'total_points', 'form', 'value_form']]

        df['element_type'] = df.element_type.map(
            self.elements_types_df.set_index('id').singular_name)

        df['team'] = df.team.map(
            self.teams_df.set_index('id').name)

        df = self.removeUnwantedTeams(df)
        df = self.removeZeroValues(df)

        return df

    def removeUnwantedTeams(self, df):
        for team in self.unwanted_teams:
            df = df.loc[df.team != team]

        return df

    def removeZeroValues(self, df):
        for column in self.higher_than_zero:
            df[column] = df[column].astype(float)
            df = df.loc[df[column] > 0]

        return df

    def createPivot(self, index, value):
        df = self.getPlayerDf()

        pivot = df.pivot_table(index=index, values=value,
                               aggfunc=np.mean).reset_index()

        pivot = pivot.sort_values(value, ascending=False)

        return pivot

    def dfFiltered(self, column, element, sort_by):
        df = self.getPlayerDf()
        df = df.loc[df[column] == element]
        df = df.sort_values(sort_by, ascending=False)

        return df