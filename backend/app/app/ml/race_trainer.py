#!/usr/bin/env python3

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier, Pool, cv, metrics
from sklearn.model_selection import train_test_split

from .clickhouse_pd import get_complete_race_df

train_df, test_df = get_complete_race_df()

train_df.fillna(-999, inplace=True)
test_df.fillna(-999, inplace=True)

x = train_df.drop(
    ["winner", "finish_position", "wagering_position", "official_position"],
    axis="columns",
)
y = train_df.winner

print(x.dtypes)

categorical_features_indices = np.where(x.dtypes != float)[0]

x_train, x_validation, y_train, y_validation = train_test_split(x, y, train_size=0.75)

x_test = test_df

model = CatBoostClassifier(custom_loss=[metrics.Accuracy()], logging_level="Silent")


model.fit(
    x_train,
    y_train,
    cat_features=categorical_features_indices,
    eval_set=(x_validation, y_validation),
    # logging_level='Verbose',
    plot=True,
)

cv_params = model.get_params()
cv_params.update(
    {"loss_function": metrics.Logloss(),}
)

cv_data = cv(
    Pool(x, y, cat_features=categorical_features_indices), cv_params, plot=True,
)

submission = pd.DataFrame()
submission["horse"] = x_test["horse"]
submission["winner"] = model.predict_proba(x_test)

print("submission", submission)

submission.to_csv("submission.csv", index=False)
