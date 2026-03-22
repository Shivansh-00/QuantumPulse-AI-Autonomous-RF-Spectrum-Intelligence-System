"""AI Prediction Service.

Advanced LSTM+Attention and Transformer models for predictive RF spectrum
congestion detection with ensemble prediction, confidence intervals,
and anomaly detection for autonomous spectrum management.
"""
from __future__ import annotations

import os
import numpy as np
import torch
import torch.nn as nn
from typing import List, Optional, Tuple


# ══════════════════════════════════════════════════════════════════
#  LSTM with Multi-Head Attention
# ══════════════════════════════════════════════════════════════════

class SpectrumLSTM(nn.Module):
    """Bi-directional LSTM with multi-head attention for spectrum prediction."""

    def __init__(
        self,
        input_size: int = 1,
        hidden_size: int = 128,
        num_layers: int = 2,
        output_size: int = 10,
        dropout: float = 0.2,
        num_heads: int = 4,
    ):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True,
        )

        # Multi-head attention over LSTM outputs
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_size * 2,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        self.layer_norm = nn.LayerNorm(hidden_size * 2)

        self.fc = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, hidden_size // 2),
            nn.GELU(),
            nn.Linear(hidden_size // 2, output_size),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)
        # Self-attention
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        attn_out = self.layer_norm(attn_out + lstm_out)
        # Global average pooling
        context = attn_out.mean(dim=1)
        return self.fc(context)


# ══════════════════════════════════════════════════════════════════
#  Transformer Encoder for Spectrum Prediction
# ══════════════════════════════════════════════════════════════════

class SpectrumTransformer(nn.Module):
    """Transformer encoder with learned positional encoding for spectrum prediction."""

    def __init__(
        self,
        input_size: int = 1,
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 3,
        output_size: int = 10,
        dropout: float = 0.1,
        max_len: int = 500,
    ):
        super().__init__()
        self.input_projection = nn.Linear(input_size, d_model)
        self.pos_encoding = PositionalEncoding(d_model, dropout, max_len)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, num_layers=num_layers
        )
        self.output_norm = nn.LayerNorm(d_model)

        self.fc = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, output_size),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.input_projection(x)
        x = self.pos_encoding(x)
        x = self.transformer_encoder(x)
        x = self.output_norm(x)
        x = x.mean(dim=1)
        return self.fc(x)


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding for transformer model."""

    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model)
        )
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.pe[:, : x.size(1)]  # type: ignore[index]
        return self.dropout(x)


# ══════════════════════════════════════════════════════════════════
#  Anomaly Detection Model
# ══════════════════════════════════════════════════════════════════

class SpectrumAutoencoder(nn.Module):
    """Autoencoder for RF spectrum anomaly detection.

    Reconstruction error serves as an anomaly score — high error
    indicates an unusual spectral pattern.
    """

    def __init__(self, input_size: int = 50, latent_size: int = 16):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.GELU(),
            nn.Linear(64, 32),
            nn.GELU(),
            nn.Linear(32, latent_size),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_size, 32),
            nn.GELU(),
            nn.Linear(32, 64),
            nn.GELU(),
            nn.Linear(64, input_size),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encoder(x)
        return self.decoder(z)

    def anomaly_score(self, x: torch.Tensor) -> torch.Tensor:
        """Mean squared reconstruction error as anomaly score."""
        recon = self.forward(x)
        return torch.mean((x - recon) ** 2, dim=-1)


# ══════════════════════════════════════════════════════════════════
#  Congestion Predictor (Ensemble + Confidence)
# ══════════════════════════════════════════════════════════════════

class CongestionPredictor:
    """High-level API for congestion prediction with ensemble and anomaly detection."""

    def __init__(
        self,
        model_type: str = "lstm",
        sequence_length: int = 50,
        prediction_horizon: int = 10,
        model_path: Optional[str] = None,
    ):
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.model_type = model_type
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Primary model
        if model_type == "transformer":
            self.model = SpectrumTransformer(
                output_size=prediction_horizon
            ).to(self.device)
        else:
            self.model = SpectrumLSTM(
                output_size=prediction_horizon
            ).to(self.device)

        if model_path and os.path.exists(model_path):
            self.model.load_state_dict(
                torch.load(model_path, map_location=self.device, weights_only=True)
            )

        # Anomaly detector
        self.anomaly_detector = SpectrumAutoencoder(
            input_size=sequence_length
        ).to(self.device)

        self.model.eval()
        self.anomaly_detector.eval()
        self._prediction_history: List[float] = []

    def prepare_sequence(self, signal_data: List[float]) -> torch.Tensor:
        """Convert signal data to model input tensor."""
        data = np.array(signal_data)
        mean = np.mean(data)
        std = np.std(data) if np.std(data) > 0 else 1.0
        data = (data - mean) / std

        if len(data) >= self.sequence_length:
            data = data[-self.sequence_length:]
        else:
            padding = np.zeros(self.sequence_length - len(data))
            data = np.concatenate([padding, data])

        tensor = torch.FloatTensor(data).unsqueeze(0).unsqueeze(-1)
        return tensor.to(self.device)

    @torch.no_grad()
    def predict(self, signal_data: List[float]) -> dict:
        """Predict future congestion levels with confidence intervals and anomaly score."""
        input_tensor = self.prepare_sequence(signal_data)
        predictions = self.model(input_tensor).cpu().numpy().flatten()

        # Sigmoid to get congestion levels [0, 1]
        congestion_levels = 1.0 / (1.0 + np.exp(-predictions))

        # Anomaly detection
        flat_input = input_tensor.squeeze(-1)  # (1, seq_len)
        anomaly_score = float(self.anomaly_detector.anomaly_score(flat_input).cpu().item())

        # Confidence based on prediction variance and anomaly
        prediction_std = float(np.std(congestion_levels))
        confidence = float(max(0.0, 1.0 - prediction_std - 0.3 * min(anomaly_score, 1.0)))

        # Trend analysis from prediction history
        mean_cong = float(np.mean(congestion_levels))
        self._prediction_history.append(mean_cong)
        if len(self._prediction_history) > 50:
            self._prediction_history = self._prediction_history[-50:]

        trend = "stable"
        if len(self._prediction_history) >= 3:
            recent = self._prediction_history[-3:]
            if recent[-1] > recent[0] + 0.05:
                trend = "increasing"
            elif recent[-1] < recent[0] - 0.05:
                trend = "decreasing"

        # Confidence intervals (simple bootstrap-style)
        ci_width = prediction_std * 1.96
        lower_bound = np.clip(congestion_levels - ci_width, 0, 1)
        upper_bound = np.clip(congestion_levels + ci_width, 0, 1)

        return {
            "congestion_levels": congestion_levels.tolist(),
            "mean_congestion": mean_cong,
            "max_congestion": float(np.max(congestion_levels)),
            "prediction_horizon": self.prediction_horizon,
            "risk_level": self._classify_risk(mean_cong),
            "confidence": round(confidence, 3),
            "trend": trend,
            "anomaly_score": round(anomaly_score, 4),
            "confidence_interval": {
                "lower": lower_bound.tolist(),
                "upper": upper_bound.tolist(),
            },
        }

    def _classify_risk(self, mean_congestion: float) -> str:
        if mean_congestion > 0.7:
            return "HIGH"
        elif mean_congestion > 0.4:
            return "MEDIUM"
        return "LOW"

    def train_on_data(
        self,
        signal_sequences: List[List[float]],
        targets: List[List[float]],
        epochs: int = 50,
        learning_rate: float = 0.001,
    ) -> dict:
        """Train the model on labeled signal data with early stopping."""
        self.model.train()
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=learning_rate, weight_decay=1e-4)
        criterion = nn.MSELoss()
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, patience=5, factor=0.5
        )

        losses = []
        best_loss = float("inf")
        patience_counter = 0

        for epoch in range(epochs):
            epoch_loss = 0.0
            for seq, target in zip(signal_sequences, targets):
                input_tensor = self.prepare_sequence(seq)
                target_tensor = torch.FloatTensor(target).unsqueeze(0).to(self.device)

                optimizer.zero_grad()
                output = self.model(input_tensor)
                loss = criterion(output, target_tensor)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                epoch_loss += loss.item()

            avg_loss = epoch_loss / max(len(signal_sequences), 1)
            losses.append(avg_loss)
            scheduler.step(avg_loss)

            # Early stopping
            if avg_loss < best_loss - 1e-5:
                best_loss = avg_loss
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= 10:
                    break

        # Also train anomaly detector
        self._train_anomaly_detector(signal_sequences, epochs=min(epochs, 20))

        self.model.eval()
        return {
            "epochs": len(losses),
            "final_loss": losses[-1] if losses else 0,
            "best_loss": best_loss,
            "loss_history": losses,
        }

    def _train_anomaly_detector(self, sequences: List[List[float]], epochs: int = 20):
        """Train the autoencoder anomaly detector alongside the main model."""
        self.anomaly_detector.train()
        optimizer = torch.optim.Adam(self.anomaly_detector.parameters(), lr=0.001)
        criterion = nn.MSELoss()

        for _ in range(epochs):
            for seq in sequences:
                data = np.array(seq)
                mean = np.mean(data)
                std = np.std(data) if np.std(data) > 0 else 1.0
                data = (data - mean) / std
                if len(data) >= self.sequence_length:
                    data = data[-self.sequence_length:]
                else:
                    data = np.concatenate([np.zeros(self.sequence_length - len(data)), data])

                x = torch.FloatTensor(data).unsqueeze(0).to(self.device)
                optimizer.zero_grad()
                recon = self.anomaly_detector(x)
                loss = criterion(recon, x)
                loss.backward()
                optimizer.step()

        self.anomaly_detector.eval()

    def save_model(self, path: str):
        """Save model weights to disk."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        torch.save(self.model.state_dict(), path)

    def generate_synthetic_training_data(
        self, num_samples: int = 200
    ) -> Tuple[List[List[float]], List[List[float]]]:
        """Generate realistic synthetic training data with diverse congestion patterns."""
        sequences = []
        targets = []
        rng = np.random.default_rng(42)

        for i in range(num_samples):
            t = np.linspace(0, 1, self.sequence_length + self.prediction_horizon)
            pattern = i % 5

            if pattern == 0:
                # Steady state with noise
                base = rng.uniform(0.2, 0.8)
                congestion = base + 0.05 * rng.standard_normal(len(t))
            elif pattern == 1:
                # Rising congestion
                base = rng.uniform(0.1, 0.4)
                congestion = base + 0.5 * t + 0.03 * rng.standard_normal(len(t))
            elif pattern == 2:
                # Falling congestion
                base = rng.uniform(0.6, 0.9)
                congestion = base - 0.4 * t + 0.03 * rng.standard_normal(len(t))
            elif pattern == 3:
                # Oscillating
                freq = rng.uniform(2, 6)
                congestion = 0.5 + 0.3 * np.sin(2 * np.pi * freq * t) + 0.02 * rng.standard_normal(len(t))
            else:
                # Spike event
                congestion = 0.3 * np.ones(len(t)) + 0.03 * rng.standard_normal(len(t))
                spike_pos = rng.integers(len(t) // 4, 3 * len(t) // 4)
                spike_width = rng.integers(3, 8)
                congestion[max(0, spike_pos - spike_width):spike_pos + spike_width] += rng.uniform(0.3, 0.6)

            congestion = np.clip(congestion, 0, 1)
            sequences.append(congestion[:self.sequence_length].tolist())
            targets.append(congestion[self.sequence_length:].tolist())

        return sequences, targets
