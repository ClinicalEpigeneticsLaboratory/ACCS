from os.path import join
from subprocess import call

import joblib
import numpy as np
import pandas as pd
import plotly.express as px
from plotly.io import write_json


class Inference:
    def __init__(
        self,
        artifacts_root: str,
        model: str,
        scaler: str,
        imputer: str,
        anomaly_detector: str,
        sesame: str,
        tasks_path: str,
        path_id: str,
    ):
        self.project = join(tasks_path, path_id)

        self.model = joblib.load(join(artifacts_root, model))
        self.scaler = joblib.load(join(artifacts_root, scaler))
        self.imputer = joblib.load(join(artifacts_root, imputer))
        self.anomaly_detector = joblib.load(join(artifacts_root, anomaly_detector))

        self.script = join(artifacts_root, sesame)

    def parse_raw_data(self) -> None:
        call(["Rscript", self.script, self.project], shell=False)

    def load_beta_values(self) -> pd.DataFrame:
        beta = pd.read_parquet(join(self.project, "mynorm.parquet"))
        return beta.set_index("CpG")

    def load_intens_values(self) -> pd.DataFrame:
        intens = pd.read_parquet(join(self.project, "intensity.parquet"))
        intens = intens.set_index("CpG")

        intens = intens.div(intens.mean())
        intens = intens.map(lambda x: np.log2(x + 1e-100))

        intens.index = [f"{probe}_intens" for probe in intens.index]

        return intens

    def load_delta_values(self, sample_frame: pd.DataFrame) -> pd.DataFrame:
        pairs = [feature for feature in self.model.feature_names_in_ if "-" in feature]

        base_cpg = [feature.split("-")[0] for feature in pairs]
        successive_cpg = [feature.split("-")[1] for feature in pairs]

        base_sample_frame = sample_frame.loc[base_cpg]
        base_sample_frame.index = pairs

        successive_sample_frame = sample_frame.loc[successive_cpg]
        successive_sample_frame.index = pairs

        deltas = successive_sample_frame - base_sample_frame
        return deltas

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
        delta = self.load_delta_values(beta)
        intens = self.load_intens_values()

        data = pd.concat((beta, delta, intens))
        data = data.loc[self.model.feature_names_in_].T

        data = self.impute(data)
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
