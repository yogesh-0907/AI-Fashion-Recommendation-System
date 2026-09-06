import streamlit as st
import pandas as pd
import plotly.express as px

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


def perform_segmentation(customers_df):
    """
    Perform K-Means customer segmentation using RFM-style
    behavioral features.
    """

    features = [
        "Days_Since_Last_Purchase",
        "Purchase_Frequency",
        "Total_Spending",
        "Average_Order_Value"
    ]

    data = customers_df[["Customer_ID"] + features].copy()

    # Remove customers with no purchase history
    data_for_clustering = data[
        data["Purchase_Frequency"] > 0
    ].copy()

    if len(data_for_clustering) < 3:
        return None, None, None

    # Prepare features
    X = data_for_clustering[features]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Find the best number of clusters using silhouette score
    best_k = 2
    best_score = -1

    for k in range(2, 7):

        if k >= len(data_for_clustering):
            break

        kmeans = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10
        )

        labels = kmeans.fit_predict(X_scaled)

        score = silhouette_score(
            X_scaled,
            labels
        )

        if score > best_score:
            best_score = score
            best_k = k

    # Final K-Means model
    kmeans = KMeans(
        n_clusters=best_k,
        random_state=42,
        n_init=10
    )

    data_for_clustering["Cluster"] = kmeans.fit_predict(X_scaled)

    # Cluster summary
    cluster_summary = (
        data_for_clustering
        .groupby("Cluster")
        .agg(
            Customer_Count=("Customer_ID", "count"),
            Avg_Recency=("Days_Since_Last_Purchase", "mean"),
            Avg_Frequency=("Purchase_Frequency", "mean"),
            Avg_Spending=("Total_Spending", "mean"),
            Avg_Order_Value=("Average_Order_Value", "mean")
        )
        .reset_index()
    )

    # --------------------------------------------------------
    # ASSIGN HUMAN-READABLE SEGMENT NAMES
    # --------------------------------------------------------

    segment_names = {}

    # Highest spending + highest frequency + recent purchases
    high_value_cluster = cluster_summary.sort_values(
        ["Avg_Spending", "Avg_Frequency"],
        ascending=False
    ).iloc[0]["Cluster"]

    # Highest recency = least recently active
    at_risk_cluster = cluster_summary.sort_values(
        "Avg_Recency",
        ascending=False
    ).iloc[0]["Cluster"]

    for cluster in cluster_summary["Cluster"]:

        if cluster == high_value_cluster:
            segment_names[cluster] = "High-Value Loyal"

        elif cluster == at_risk_cluster:
            segment_names[cluster] = "At-Risk / Inactive"

        else:
            segment_names[cluster] = "Regular Customers"

    data_for_clustering["Segment"] = (
        data_for_clustering["Cluster"]
        .map(segment_names)
    )

    cluster_summary["Segment"] = (
        cluster_summary["Cluster"]
        .map(segment_names)
    )

    return (
        data_for_clustering,
        cluster_summary,
        best_score
    )


def display_clusters():

    st.subheader("Customer Segmentation")

    try:
        customers_df = pd.read_csv(
            "data/CUSTOMERS.csv"
        )
    except Exception as e:
        st.error(
            f"Failed to load customer data: {e}"
        )
        return

    if customers_df.empty:
        st.warning("No customer data available.")
        return

    segmented_data, cluster_summary, silhouette = (
        perform_segmentation(customers_df)
    )

    if segmented_data is None:
        st.warning(
            "Insufficient customer purchase data for clustering."
        )
        return

    # --------------------------------------------------------
    # RESULTS
    # --------------------------------------------------------

    st.write(
        f"Discovered **{len(cluster_summary)} customer segments** "
        f"using K-Means clustering."
    )

    st.metric(
        "Silhouette Score",
        f"{silhouette:.3f}"
    )

    # --------------------------------------------------------
    # CLUSTER SUMMARY
    # --------------------------------------------------------

    st.subheader("Segment Summary")

    st.dataframe(
        cluster_summary.round(2),
        use_container_width=True
    )

    # --------------------------------------------------------
    # VISUALIZATION
    # --------------------------------------------------------

    fig = px.scatter(
        segmented_data,
        x="Purchase_Frequency",
        y="Total_Spending",
        color="Cluster",
        size="Average_Order_Value",
        hover_data=[
            "Customer_ID",
            "Days_Since_Last_Purchase"
        ],
        title="Customer Segments",
        labels={
            "Purchase_Frequency": "Purchase Frequency",
            "Total_Spending": "Total Spending (₹)",
            "Cluster": "Segment"
        }
    )

    fig.update_layout(
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------------------------------------
    # CUSTOMER SEGMENT TABLE
    # --------------------------------------------------------

    st.subheader("Customer Segment Assignments")

    st.dataframe(
        segmented_data[
            [
                "Customer_ID",
                "Days_Since_Last_Purchase",
                "Purchase_Frequency",
                "Total_Spending",
                "Average_Order_Value",
                "Cluster"
            ]
        ].sort_values("Cluster"),
        use_container_width=True
    )