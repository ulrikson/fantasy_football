from Fantasy import Fantasy
from tabulate import tabulate


class Alternative:
    def __init__(self, player, league):
        self.player = player
        self.league = league

        self.df_all = self.__get_base_df()
        self.df_alternatives = self.df_all  # initially
        self.player_stats = self.__get_player_stats()

    def __get_base_df(self):
        fantasy = Fantasy(self.league, [], {}, 2000)
        df = fantasy.get_player_df(False, True)
        return df

    def __get_player_stats(self):
        df = self.df_all
        player_stats = df[df["web_name"] == self.player]
        return player_stats

    def better_choice(self, same_position):
        self.__filter_by_availability()

        if same_position:
            self.__filter_by_position()

        self.__filter_by_cost()
        self.__filter_by_form()
        self.__filter_by_ep()

        self.__print_results()

    def __filter_by_availability(self):
        # a player must be 100% available to be interesting
        df = self.df_alternatives
        df = df[df["chance_of_playing_next_round"] == 100]

        self.df_alternatives = df

    def __filter_by_position(self):
        position = self.player_stats["element_type"].iloc[0]

        df = self.df_alternatives
        df = df[df["element_type"] == position]

        self.df_alternatives = df

    def __filter_by_cost(self):
        cost = self.player_stats["now_cost"].iloc[0]

        df = self.df_alternatives
        df = df[df["now_cost"] <= cost]

        self.df_alternatives = df

    def __filter_by_form(self):
        # player should have at least the same form
        form = self.player_stats["form"].iloc[0]

        df = self.df_alternatives
        df = df[df["form"] >= form]

        self.df_alternatives = df

    def __filter_by_ep(self):
        # player should have at least as many expected points
        ep_next = self.player_stats["ep_next"].iloc[0]

        df = self.df_alternatives
        df = df[df["ep_next"] >= ep_next]

        self.df_alternatives = df

    def __print_results(self):
        headers = ["web_name", "ep_next", "form", "now_cost", "value_season_adj"]
        df = self.df_alternatives[headers]
        df = df.sort_values("ep_next", ascending=False)
        df["now_cost"] = df["now_cost"] / 10

        print(tabulate(df, headers=headers, showindex=False, tablefmt="github"))


Alternative("Bowen", "fpl").better_choice(same_position=True)
