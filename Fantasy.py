import pandas as pd
import numpy as np
import requests

import matplotlib.pyplot as plt

plt.style.use("ggplot")

import seaborn as sns

sns.set_theme(color_codes=True)
sns.set(rc={"figure.figsize": (20, 10)})

import warnings

warnings.filterwarnings("ignore")


class Fantasy:
    def __init__(self, league, unwanted_teams, higher_than, max_cost):
        self.league = league

        self.json = self.getJson()
        self.elements_df = pd.DataFrame(self.json["elements"])
        self.elements_types_df = pd.DataFrame(self.json["element_types"])
        self.teams_df = pd.DataFrame(self.json["teams"])

        self.unwanted_teams = unwanted_teams
        self.higher_than = higher_than
        self.max_cost = max_cost

    def getJson(self):
        if self.league == "fpl":
            url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        else:
            url = "https://fantasy.allsvenskan.se/api/bootstrap-static/"

        response = requests.get(url)
        json = response.json()

        return json

    def getPlayerDf(self):
        df = self.elements_df[
            [
                "web_name",
                "team",
                "element_type",
                "points_per_game",
                "now_cost",
                "minutes",
                "value_season",
                "total_points",
                "form",
                "value_form",
            ]
        ]

        df["element_type"] = df.element_type.map(
            self.elements_types_df.set_index("id").singular_name
        )

        df["team"] = df.team.map(self.teams_df.set_index("id").name)

        df["element_type"] = df["element_type"].replace(
            {
                "Målvakt": "Goalkeeper",
                "Försvarare": "Defender",
                "Mittfältare": "Midfielder",
                "Anfallare": "Forward",
            }
        )

        df = self.removeUnwantedTeams(df)
        df = self.stringToFloat(df)

        df["value_season_adj"] = df["value_season"] / (
            df["total_points"] / df["points_per_game"]
        )

        df = df[df["now_cost"] < self.max_cost]

        df = self.removeLowValues(df)

        return df

    def removeUnwantedTeams(self, df):
        for team in self.unwanted_teams:
            df = df.loc[df.team != team]

        return df

    def stringToFloat(self, df):
        columnsShouldBeFloat = [
            "points_per_game",
            "now_cost",
            "minutes",
            "value_season",
            "total_points",
            "form",
            "value_form",
        ]
        for column in columnsShouldBeFloat:
            df[column] = df[column].astype(float)

        return df

    def removeLowValues(self, df):
        for key, value in self.higher_than.items():
            df = df.loc[df[key] > value]

        return df

    def createPivot(self, index, value):
        df = self.getPlayerDf()

        pivot = df.pivot_table(index=index, values=value, aggfunc=np.mean).reset_index()

        pivot = pivot.sort_values(value, ascending=False)

        return pivot

    def dfFiltered(self, column, element, sort_by):
        df = self.getPlayerDf()
        df = df.loc[df[column] == element]
        df = df.sort_values(sort_by, ascending=False)

        return df

    def getTopTeam(self):
        gk_df = self.dfFiltered("element_type", "Goalkeeper", "value_season_adj").head(
            2
        )
        def_df = self.dfFiltered("element_type", "Defender", "value_season_adj").head(5)
        mid_df = self.dfFiltered("element_type", "Midfielder", "value_season_adj").head(
            5
        )
        fwd_df = self.dfFiltered("element_type", "Forward", "value_season_adj").head(3)

        top = gk_df.append(def_df).append(mid_df).append(fwd_df)

        return top

    def getBarPlot(self, column, element):
        pivot = self.createPivot(column, element).sort_values(element)

        pivot.plot(kind="barh", x=column, figsize=(10, 6))

    def getPlayerScatterPlot(self, position, x, y, regline):
        df = self.dfFiltered("element_type", position, "value_season_adj")

        if regline:
            ax = sns.regplot(x=x, y=y, data=df)
        else:
            ax = sns.scatterplot(x=x, y=y, data=df)

        for i, txt in enumerate(df.web_name):
            ax.annotate(txt, (df[x].iat[i], df[y].iat[i]))

    def getMVPScatterPlot(self):
        x = "total_points"
        y = "value_season_adj"

        top_gk = self.dfFiltered("element_type", "Goalkeeper", x).head()
        top_def = self.dfFiltered("element_type", "Defender", x).head()
        top_mid = self.dfFiltered("element_type", "Midfielder", x).head()
        top_fwd = self.dfFiltered("element_type", "Forward", x).head()

        ax = top_gk.plot.scatter(
            x=x,
            y=y,
            color="DarkBlue",
            label="GK",
            s=top_gk[x],
            alpha=0.5,
            figsize=(15, 10),
            title="Top 5 Players by Position",
        )

        for i, txt in enumerate(top_gk.web_name):
            ax.annotate(txt, (top_gk[x].iat[i], top_gk[y].iat[i]))

        top_def.plot.scatter(
            x=x, y=y, color="DarkGreen", label="DEF", s=top_gk[x], ax=ax
        )
        for i, txt in enumerate(top_def.web_name):
            ax.annotate(txt, (top_def[x].iat[i], top_def[y].iat[i]))

        top_mid.plot.scatter(
            x=x, y=y, color="DarkOrange", label="MID", s=top_gk[x], ax=ax
        )
        for i, txt in enumerate(top_mid.web_name):
            ax.annotate(txt, (top_mid[x].iat[i], top_mid[y].iat[i]))

        top_fwd.plot.scatter(x=x, y=y, color="DarkRed", label="FWD", s=top_gk[x], ax=ax)
        for i, txt in enumerate(top_fwd.web_name):
            ax.annotate(txt, (top_fwd[x].iat[i], top_fwd[y].iat[i]))
