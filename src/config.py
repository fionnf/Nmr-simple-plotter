"""Configuration schema and loader for NMR plotter using Pydantic."""

from typing import Optional, List, Dict, Any, Literal, Tuple
from pathlib import Path
import yaml
from pydantic import BaseModel, Field, field_validator


class PhaseConfig(BaseModel):
    """Phase correction configuration."""
    auto: bool = False
    phase0: float = 0.0
    phase1: float = 0.0
    entropy_method: Literal["fwhm", "hybrid"] = "hybrid"


class BaselineConfig(BaseModel):
    """Baseline correction configuration."""
    method: Literal["none", "polynomial", "airpls", "spline"] = "polynomial"
    poly_order: int = Field(3, ge=1, le=5)


class SmoothingConfig(BaseModel):
    """Spectral smoothing configuration."""
    method: Literal["none", "savgol", "moving_average", "gaussian"] = "none"
    window_length: int = 11
    poly_order: int = 3


class PeakPickingConfig(BaseModel):
    """Peak detection and annotation configuration."""
    enabled: bool = False
    threshold: float = Field(0.05, ge=0.0, le=1.0)
    min_distance: float = 10.0
    annotate: bool = True


class ProcessingConfig(BaseModel):
    """Data processing pipeline configuration."""
    phase: PhaseConfig = Field(default_factory=PhaseConfig)
    baseline: BaselineConfig = Field(default_factory=BaselineConfig)
    smoothing: SmoothingConfig = Field(default_factory=SmoothingConfig)
    peak_picking: PeakPickingConfig = Field(default_factory=PeakPickingConfig)


class PlotConfig(BaseModel):
    """Configuration for a single plot."""
    file: str
    label: str = ""
    color: Optional[str] = None
    linewidth: float = 1.5
    linestyle: Literal["solid", "dashed", "dotted"] = "solid"
    alpha: float = Field(0.9, ge=0.0, le=1.0)


class FigureStyleConfig(BaseModel):
    """Figure styling configuration."""
    template: Literal["nature", "jacs", "custom"] = "nature"
    font_family: str = "sans-serif"
    font_size: int = 10
    dpi: int = 300


class FigureConfig(BaseModel):
    """Figure configuration."""
    title: Optional[str] = None
    xlim: Optional[Tuple[float, float]] = None
    ylim: Optional[Tuple[float, float]] = None
    xlabel: str = "Chemical Shift (ppm)"
    ylabel: str = "Intensity (a.u.)"
    grid: bool = True
    legend_position: str = "upper right"
    legend_frameon: bool = True
    legend_fontsize: int = 9


class AnalysisLinewidthConfig(BaseModel):
    """Linewidth analysis configuration."""
    enabled: bool = False
    method: Literal["fwhm"] = "fwhm"
    peak_region: Optional[Tuple[float, float]] = None
    report_csv: Optional[str] = None


class AnalysisSNRConfig(BaseModel):
    """SNR analysis configuration."""
    enabled: bool = False
    signal_region: Optional[Tuple[float, float]] = None
    noise_region: Optional[Tuple[float, float]] = None
    report_csv: Optional[str] = None


class AnalysisConfig(BaseModel):
    """Analysis configuration."""
    linewidth: AnalysisLinewidthConfig = Field(default_factory=AnalysisLinewidthConfig)
    snr: AnalysisSNRConfig = Field(default_factory=AnalysisSNRConfig)


class Config(BaseModel):
    """Root configuration schema for NMR plotter."""

    # Experiment metadata
    experiment_id: Optional[str] = None
    date: Optional[str] = None

    # Data source
    data_file: str
    data_format: Literal["spinsolve_h5", "bruker_fid", "csv", "txt"] = "csv"

    # Processing
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)

    # Plotting
    plots: List[PlotConfig] = Field(default_factory=list)
    figure_style: FigureStyleConfig = Field(default_factory=FigureStyleConfig)
    figure: FigureConfig = Field(default_factory=FigureConfig)

    # Analysis
    analysis: AnalysisConfig = Field(default_factory=AnalysisConfig)

    # Output
    output_dir: str = "figures"
    output_formats: List[Literal["png", "pdf", "svg"]] = Field(default_factory=lambda: ["pdf", "png"])

    @field_validator("output_dir")
    @classmethod
    def validate_output_dir(cls, v):
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

    @classmethod
    def from_yaml(cls, filepath: str) -> "Config":
        """Load configuration from a YAML file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Load configuration from a dictionary."""
        return cls(**data)

    def to_yaml(self, filepath: str) -> None:
        """Save configuration to a YAML file."""
        with open(filepath, 'w') as f:
            yaml.dump(self.model_dump(exclude_none=False), f, default_flow_style=False)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump(exclude_none=False)
