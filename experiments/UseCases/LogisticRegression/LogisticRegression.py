import numpy as np
from mpyc.runtime import mpc
from sklearn import datasets
from sklearn.linear_model import LogisticRegression as LogisticRegressionSK

import tno.mpc.mpyc.secure_learning.test.plaintext_utils.plaintext_objective_functions as plain_obj
from tno.mpc.mpyc.secure_learning import (
    ClassWeightsTypes,
    ExponentiationTypes,
    Logistic,
    PenaltyTypes,
    SolverTypes,
)

# Notice that we use the entire dataset to train the model
n_samples = 100
n_features = 3
# Fixed random state for reproducibility
random_state = 3
tolerance = 1e-4


secnum = mpc.SecFxp(l=64, f=32)


def get_mpc_data(X, y):
    X_mpc = [[secnum(x, integral=False) for x in row] for row in X.tolist()]
    y_mpc = [secnum(y, integral=False) for y in y.tolist()]
    return X_mpc, y_mpc


def distribute_data_over_players(X_mpc, y_mpc):
    X_shared = [mpc.input(row, senders=0) for row in X_mpc]
    y_shared = mpc.input(y_mpc, senders=0)
    return X_shared, y_shared


def sklearn_class_weights_dict(y):
    n_class_1 = sum([((y_i + 1) / 2) for y_i in y])
    n_class_0 = len(y) - n_class_1

    w_0 =  len(y) / (2 * n_class_0)
    w_1 = len(y) / (2 * n_class_1)

    return {-1: w_0, 1: w_1}


async def logistic_regression_example():
    print(
        "Classification (Logistic regression) with l1 penalty, with gradient descent method"
    )
    alpha = 0.1

    # Create classification dataset
    X, y = datasets.make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_informative=1,
        n_redundant=0,
        n_classes=2,
        n_clusters_per_class=1,
        random_state=random_state,
        shift=0,
        weights=[0.25, 0.75],
    )
    # Transform labels from {0, 1} to {-1, +1}.
    y = [-1 if x == 0 else 1 for x in y]
    X = np.array(X)
    y = np.array(y)
    X_mpc, y_mpc = get_mpc_data(X, y)

    async with mpc:
        X_shared, y_shared = distribute_data_over_players(X_mpc, y_mpc)

    # Train secure model with approximation of logistic function (faster, less accurate)
    model = Logistic(
        solver_type=SolverTypes.GD,
        exponentiation=ExponentiationTypes.APPROX,
        penalty=PenaltyTypes.L1,
        alpha=alpha,
        class_weights_type=ClassWeightsTypes.BALANCED,
    )
    async with mpc:
        coef_approx = await model.compute_coef_mpc(
            X_shared, y_shared, tolerance=tolerance
        )

    async with mpc:
        class_weights_dict =  model.reveal_class_weights(y_shared)

    # Results of secure model (approximated logistic function)
    objective_approx = plain_obj.objective(
        X, y, coef_approx, "logistic", PenaltyTypes.L1, alpha, class_weights_dict
    )
    print(
        "Securely obtained coefficients (approximated exponentiation):",
        coef_approx,
    )
    print("* objective:", objective_approx)
    print("Class weights dictionary:", class_weights_dict)
    # Train secure model with exact logistic function (slower, more accurate)
    model = Logistic(
        solver_type=SolverTypes.GD,
        exponentiation=ExponentiationTypes.EXACT,
        penalty=PenaltyTypes.L1,
        alpha=alpha,
        class_weights_type=ClassWeightsTypes.BALANCED,
    )
    async with mpc:
        coef_exact = await model.compute_coef_mpc(
            X_shared, y_shared, tolerance=tolerance
        )

    # Results of secure model (exact logistic function)
    objective_exact = plain_obj.objective(
        X,
        y,
        coef_exact,
        "logistic",
        PenaltyTypes.L1,
        alpha,
        class_weights_dict,
    )
    print(
        "Securely obtained coefficients (exact exponentiation):       ",
        coef_exact,
    )
    print("* objective:", objective_exact)
    print("Class weights dictionary:", class_weights_dict)
    # Train plaintext model
    model_sk = LogisticRegressionSK(
        solver="saga",
        random_state=random_state,
        fit_intercept=True,
        penalty="l1",
        C=1 / (len(X) * alpha),
        class_weight="balanced",
    )

    class_weights_dict_sk = sklearn_class_weights_dict(y)
    model_sk.fit(X, y)
    coef_sk = np.append([model_sk.intercept_], model_sk.coef_).tolist()

    # Results of plaintest model
    objective_sk = plain_obj.objective(
        X, y, coef_sk, "logistic", PenaltyTypes.L1, alpha
    )
    print("Sklearn obtained coefficients:                               ", coef_sk)
    print("* objective:", objective_sk)


if __name__ == "__main__":
    mpc.run(logistic_regression_example())