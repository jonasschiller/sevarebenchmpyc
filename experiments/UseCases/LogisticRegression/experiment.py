import numpy as np
from mpyc.runtime import mpc
from sklearn import datasets
from sklearn.linear_model import LogisticRegression as LogisticRegressionSK


# Notice that we use the entire dataset to train the model
n_samples = 10000
n_features = 20
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

def training(X_shared, y_shared, alpha):
    # Initialize weights
    weights = [secnum(0, integral=False) for _ in range(n_features)]
    # Perform training step of logistic regression
    for _ in range(100):
        weights = logistic_regression_step(X_shared, y_shared, weights, alpha)
    return weights

def logistic_regression_step(X_shared, y_shared, weights, alpha):
    # Compute gradient
    gradient = compute_gradient(X_shared, y_shared, weights)
    # Update weights
    weights = update_weights(weights, gradient[0], alpha)
    return weights

def compute_gradient(X_shared, y_shared, weights):
    # Compute gradient
    gradient = [secnum(0, integral=False) for _ in range(n_features)]
    dot_product= mpc.matrix_prod(X_shared, [[_] for _ in weights], False)
    dot_product = [x for [x] in dot_product]
    # Compute approximated sigmoid using relu plus
    d_0 = [x < secnum(-0.5)  for x in dot_product]
    d_1 = [x > secnum(0.5) for x in dot_product]

    sigmoid = [
        d_1[i]
        + (secnum(1) - d_0[i]) * (secnum(1) - d_1[i]) * (dot_product[i] + secnum(0.5))
        for i in range(len(d_0))
    ]
    gradient = mpc.matrix_prod(mpc.matrix_sub([sigmoid],[y_shared]), X_shared, False)
    return gradient

def update_weights(weights, gradient, alpha):
    # Update weights
    for j in range(n_features):
        weights[j] = weights[j] - alpha * gradient[j]
    return weights

def predict(X_shared, weights):
    # Predict
    y_pred = [secnum(0, integral=False) for _ in range(n_samples)]
    dot_product= mpc.matrix_prod(X_shared, [[_] for _ in weights], False)
    dot_product = [x for [x] in dot_product]
    # Compute approximated sigmoid using relu plus
    d_0 = [x < secnum(-0.5)  for x in dot_product]
    d_1 = [x > secnum(0.5) for x in dot_product]

    sigmoid = [
        d_1[i]
        + (secnum(1) - d_0[i]) * (secnum(1) - d_1[i]) * (dot_product[i] + secnum(0.5))
        for i in range(len(d_0))
    ]
    print(len(sigmoid))
    for i in range(n_samples):
        y_pred[i] = mpc.if_else(sigmoid[i] > secnum(0.5, integral=False), secnum(1, integral=False), secnum(0, integral=False))
    return y_pred

def compute_accuracy(y_pred, y_shared):
    # Compute accuracy
    accuracy = 0
    for i in range(n_samples):
        accuracy += mpc.if_else(y_pred[i] == y_shared[i], secnum(1, integral=False), secnum(0, integral=False))
    accuracy = accuracy / n_samples
    return accuracy

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
    
    X = np.array(X)
    y = np.array(y)
    X_mpc, y_mpc = get_mpc_data(X, y)

    await mpc.start()
    X_shared, y_shared = distribute_data_over_players(X_mpc, y_mpc)
    # Perform training step of logistic regression
    weights= training(X_shared, y_shared, alpha)
    y_pred = predict(X_shared, weights)
    accuracy = compute_accuracy(y_pred, y_shared)
    
    print("Accuracy: ", await mpc.output(accuracy))
    await mpc.shutdown()

   


if __name__ == "__main__":
    mpc.run(logistic_regression_example())