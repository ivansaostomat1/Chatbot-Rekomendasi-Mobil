from sklearn.metrics import silhouette_score
from clustering.agglomerative import build_feature_matrix
from vikor.ranking_engine import DF_CARS

def evaluate_clustering():

    X, _ = build_feature_matrix(DF_CARS)

    labels = DF_CARS["CLUSTER_ID"]

    score = silhouette_score(X, labels)

    print("Silhouette Score:", score)


if __name__ == "__main__":
    evaluate_clustering()