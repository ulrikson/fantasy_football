import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

plt.style.use("ggplot")
sns.set_theme(color_codes=True)
warnings.filterwarnings("ignore")


class Base:
    def __init__(self, league):
        self.players_df = pd.read_csv("data/players_" + league + ".csv")

    def df_filtered(self, column, element, sort_by):
        df = self.get_player_df()
        df = df.loc[df[column] == element]
        df = df.sort_values(sort_by, ascending=False)

        return df

    def get_player_df(self, all_columns=False):
        if all_columns:
            df = self.players_df
        else:
            df = self.__get_relevant_columns()

        return df

    def __get_relevant_columns(self):
        columns = [
            "web_name",
            "team",
            "element_type",
            "points_per_game",
            "now_cost",
            "minutes",
            "value_season",
            "total_points",
            "form",
            "value_season_adj",
        ]

        if self.league == "fpl":
            columns.append("ict_index")

        df = self.players_df[columns]

        return df


class Table(Base):
    def __init__(self, league):
        super().__init__(league)
        self.league = league

    def get_top_performers(self):
        df = self.get_player_df()

        if self.league == "fpl":
            form_top_value = df["form"].quantile(q=0.9)
            value_top_value = df["value_season_adj"].quantile(q=0.9)
            ict_top_value = df["ict_index"].quantile(q=0.9)

            df = df[
                (df["form"] >= form_top_value)
                & (df["value_season_adj"] >= value_top_value)
                & (df["ict_index"] >= ict_top_value)
            ]
        else:
            form_top_value = df["form"].quantile(q=0.95)
            value_top_value = df["value_season_adj"].quantile(q=0.95)
            df = df[
                (df["form"] >= form_top_value)
                & (df["value_season_adj"] >= value_top_value)
            ]

        return df.sort_values(by=["element_type", "team"], ascending=False)

    def get_top_points(self):
        df = self.get_player_df().sort_values("total_points", ascending=False).head(3)

        return df


class Graph(Base):
    def __init__(self, league):
        super().__init__(league)
        self.league = league

    def get_bar_plot(self, column, element):
        pivot = self.__create_pivot(column, element).sort_values(element)

        fig = plt.gcf()
        fig.set_size_inches(8, 4)

        sns.barplot(x=element, y=column, data=pivot)

    def __create_pivot(self, index, value):
        df = self.get_player_df()

        pivot = df.pivot_table(index=index, values=value, aggfunc=np.mean).reset_index()

        pivot = pivot.sort_values(value, ascending=False)

        return pivot

    def get_player_scatterplot(self, position, x, y, regline=False):
        df = self.df_filtered("element_type", position, "value_season_adj")

        min = df["now_cost"].min()
        max = df["now_cost"].max()

        fig = plt.gcf()
        fig.set_size_inches(20, 10)

        if regline:
            correlation_coefficient = df[x].corr(df[y])
            print("p: " + str(correlation_coefficient))
            ax = sns.regplot(x=x, y=y, data=df)
        else:
            ax = sns.scatterplot(
                x=x, y=y, data=df, size="now_cost", sizes=(min, max), hue="team"
            )

            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

        for i, txt in enumerate(df.web_name):
            ax.annotate(txt, (df[x].iat[i], df[y].iat[i]))

    def get_mvp_scatterplot(self):
        x = "form"
        y = "value_season_adj"

        top_gk = self.df_filtered("element_type", "Goalkeeper", "total_points").head()
        top_def = self.df_filtered("element_type", "Defender", "total_points").head()
        top_mid = self.df_filtered("element_type", "Midfielder", "total_points").head()
        top_fwd = self.df_filtered("element_type", "Forward", "total_points").head()

        df = top_gk.append(top_def).append(top_mid).append(top_fwd)

        min = df["now_cost"].min()
        max = df["now_cost"].max()

        ax = sns.scatterplot(
            x=x, y=y, data=df, hue="element_type", size="now_cost", sizes=(min, max)
        )

        fig = plt.gcf()
        fig.set_size_inches(20, 10)

        for i, txt in enumerate(df.web_name):
            ax.annotate(txt, (df[x].iat[i], df[y].iat[i]))
