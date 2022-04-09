from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score


class ML:
    def __init__(self, df, dependent, independents):
        self.df = df
        self.dependent = dependent
        self.independents = independents

    def __fit_linear_regression(self):
        X = self.df[self.independents]
        y = self.df[self.dependent]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, shuffle=True, train_size=0.3
        )

        model = LinearRegression()
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)
        r2 = r2_score(y_test, predictions)
        print("r2: " + str(r2))
        print(model.coef_)
        print(model.intercept_)

        return model

    def linear_regression(self):
        self.__fit_linear_regression()


from Fantasy import Fantasy

league = "fpl"

unwanted_teams = []

higher_than = {
    "value_season": 0,
    "value_season_adj": 0,
    "form": 0,
    "minutes": 0,
    "points_per_game": 0,
}

max_cost = 200

fantasy = Fantasy(league, unwanted_teams, higher_than, max_cost)

df = fantasy.get_player_df()

ML(df, "total_points", ["now_cost", "ict_index", "value_season_adj"]).linear_regression()
