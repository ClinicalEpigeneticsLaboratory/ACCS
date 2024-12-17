from os.path import join
from subprocess import call

from django.conf import settings

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.io import write_json
from scipy.spatial import cKDTree


class Inference:
    def __init__(
        self,
        artifacts_path: str,
        tasks_path: str,
        path_id: str,
        model: str,
        scaler: str,
        imputer: str,
        anomaly_detector: str,
        workflow: str,
        manifest: str,
    ):
        self.project = join(settings.MEDIA_ROOT, tasks_path, path_id)
        self.model = joblib.load(join(artifacts_path, model))
        self.scaler = joblib.load(join(artifacts_path, scaler))
        self.imputer = joblib.load(join(artifacts_path, imputer))
        self.anomaly_detector = joblib.load(join(artifacts_path, anomaly_detector))
        self.workflow = join(artifacts_path, workflow)
        self.manifest = pd.read_parquet(join(artifacts_path, manifest))

    def parse_raw_data(self) -> None:
        call(["Rscript", self.workflow, self.project], shell=False)

    def load_beta_values(self) -> pd.DataFrame:
        beta = pd.read_parquet(join(self.project, "mynorm.parquet"))
        return beta.set_index("CpG")

    @staticmethod
    def global_norm(data: pd.DataFrame) -> pd.DataFrame:
        normalized = data.div(data.mean())
        normalized = normalized.map(lambda x: np.log2(x))
        normalized.index = [f"{cpg}g" for cpg in normalized.index]
        return normalized

    def local_norm(self, mynorm: pd.DataFrame, window: int = 1000) -> pd.DataFrame:
        common_cpgs = self.manifest.index.intersection(mynorm.index)

        # Filter both DataFrames to keep only common CpGs
        manifest = self.manifest.loc[common_cpgs]
        mynorm = mynorm.loc[common_cpgs]

        # Sort manifest by chromosome and position
        manifest = manifest.sort_values(["CHR", "MAPINFO"])

        # Initialize standardized DataFrame
        normalized = mynorm.copy()

        # Process each chromosome independently
        for chr_name, chr_df in manifest.groupby("CHR"):
            # Extract positions and indices for the current chromosome
            positions = chr_df["MAPINFO"].values
            cpg_indices = chr_df.index

            # Using cKDTree for efficient local window lookup
            tree = cKDTree(positions.reshape(-1, 1))

            for idx, pos in zip(cpg_indices, positions):
                # Query for indices within the window range
                indices_within_window = tree.query_ball_point([pos], r=window)

                if len(indices_within_window) == 1:
                    continue

                window_indices = cpg_indices[indices_within_window]
                local_mean = mynorm.loc[window_indices].mean(axis=0)
                normalized.loc[idx] = np.log2((mynorm.loc[idx] / local_mean))

        normalized.index = [f"{cpg}l" for cpg in normalized.index]
        return normalized

    def impute(self, data: pd.DataFrame) -> pd.DataFrame:
        if not any(data.isna()):
            print(f"NaN not in data, skipping imputation.")
            return data

        data = data[self.scaler.feature_names_in_]

        scaled_data = self.scaler.transform(data)
        scaled_data = pd.DataFrame(scaled_data, index=data.index, columns=data.columns)
        scaled_data = scaled_data[self.imputer.feature_names_in_]

        imputed_data = self.imputer.transform(scaled_data)
        imputed_data = self.scaler.inverse_transform(imputed_data)
        imputed_data = pd.DataFrame(
            imputed_data, index=data.index, columns=data.columns
        )

        return imputed_data

    def predict(self, sample: pd.DataFrame) -> tuple:
        return (
            self.model.predict(sample)[0],
            self.model.predict_proba(sample).flatten().tolist(),
            self.model.classes_.tolist(),
        )

    def anomaly_detection(
        self, sample: pd.DataFrame, baseline_threshold: float = 1.5
    ) -> tuple:
        anomaly_score = abs(self.anomaly_detector.score_samples(sample)[0])
        threshold = abs(self.anomaly_detector["localoutlierfactor"].offset_)

        if anomaly_score >= threshold:
            status = "High-risk sample"

        elif baseline_threshold < anomaly_score < threshold:
            status = "Medium-risk sample"

        else:
            status = "Low-risk sample"

        return (
            status,
            anomaly_score,
            {"Medium-risk sample": baseline_threshold, "High-risk sample": threshold},
        )

    @staticmethod
    def asses_confidence_status(proba: float) -> str:
        if proba > 0.8:
            return "High"
        elif 0.65 < proba < 0.8:
            return "Medium"
        elif 0.5 < proba < 0.65:
            return "Low"
        else:
            return "Uncertain"

    @staticmethod
    def probability_plot(classes: list, probabilities: list, n_top: int = 10):
        df = pd.concat(
            (
                pd.Series(classes, name="Class"),
                pd.Series(probabilities, name="Probability"),
            ),
            axis=1,
        )
        df = df.sort_values("Probability", ascending=False).iloc[:n_top]

        fig = px.bar(
            data_frame=df,
            x="Probability",
            y="Class",
            orientation="h",
            title="Prediction probabilities [TOP10]",
        )
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis={"range": (0, 1)},
            yaxis={"categoryorder": "total ascending"},
        )
        for t, name in zip(
            [0.5, 0.65, 0.8],
            [
                "Low",
                "Medium",
                "High",
            ],
        ):
            fig.add_vline(
                x=t,
                line_color="red",
                line_width=2,
                line_dash="dot",
                annotation_text=name,
            )
        return fig

    @staticmethod
    def anomaly_plot(scores: float, thresholds: dict):
        fig = px.bar(x=["Sample"], y=[scores], title="Anomaly score")

        for name, value in thresholds.items():
            fig.add_hline(
                y=value,
                line_color="red",
                line_width=2,
                line_dash="dot",
                annotation_text=name,
            )

        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Anomaly score",
        )
        return fig

    def start(self) -> tuple:
        self.parse_raw_data()

        beta = self.load_beta_values()
        beta_g_norm = self.global_norm(beta)
        beta_l_norm = self.local_norm(beta)

        data = pd.concat((beta, beta_g_norm, beta_l_norm)).T
        data = self.impute(data)

        data = data[self.model.feature_names_in_]
        data.to_parquet(join(self.project, "sample.parquet"))

        prediction, confidence, classes = self.predict(data)
        confidence_status = self.asses_confidence_status(max(confidence))
        anomaly_status, anomaly_score, anomaly_t = self.anomaly_detection(data)

        pp = self.probability_plot(classes, confidence)
        write_json(pp, join(self.project, "pp.json"))

        ap = self.anomaly_plot(anomaly_score, anomaly_t)
        write_json(ap, join(self.project, "ap.json"))

        return (
            prediction,
            confidence,
            confidence_status,
            classes,
            anomaly_status,
            anomaly_score,
            anomaly_t,
        )
