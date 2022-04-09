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
        adj_r2 = 1 - (1-model.score(X, y))*(len(y)-1)/(len(y)-X.shape[1]-1)
        print("r2: " + str(r2))
        print("Adjusted r2: " + str(adj_r2))

        return model

    def predict_linear_regression(self):
        self.__fit_linear_regression()
