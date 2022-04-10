from Fantasy import Fantasy


class Optimize:
    def __init__(self, league, current_team, in_bank):
        self.current_team = current_team
        self.league = league
        self.in_bank = in_bank * 10 # due to now_cost
        self.df = self.__current_players_df()

    def find_substitutions(self):
        suggested_sub_in = []

        # at risk players are prioritized to be substituted
        at_risk = self.__players_at_risk()

        # look for alternatives to the at risk players
        # need to get the position and then get the best player in that position (function) for the same money (+ bank)

    def __players_at_risk(self):
        df = self.df[self.df["chance_of_playing_next_round"] < 100]

        return df["web_name"].tolist()

    def __current_players_df(self):
        df = self.__base_df()
        df = df.loc[df["web_name"].isin(self.current_team)]

        return df

    def __base_df(self):
        df = Fantasy(self.league, [], {}, 2000).get_player_df(False, True)
        return df


current_team = [
    "Guaita",
    "Raya",
    "Doherty",
    "Alexander-Arnold",
    "Cancelo",
    "Andersen",
    "Robertson",
    "Bowen",
    "Benrahma",
    "Kulusevski",
    "De Bruyne",
    "Son",
    "Pukki",
    "Toney",
    "Mateta",
]

in_bank = 0.1

Optimize("fpl", current_team, in_bank).find_substitutions()
