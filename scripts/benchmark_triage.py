#!/usr/bin/env python3
"""Benchmark AI triage engine accuracy against ground truth dataset.

This script evaluates the triage engine's classification accuracy by:
1. Loading a curated dataset of security findings with ground truth labels
2. Running the triage engine on each finding
3. Comparing predictions against ground truth
4. Calculating accuracy metrics (overall, per-CWE, precision, recall, F1)
5. Generating a detailed benchmark report with failure analysis

Usage:
    python scripts/benchmark_triage.py \\
        --dataset tests/fixtures/benchmark_dataset/ground_truth.json \\
        --report docs/reports/triage-benchmark.md
"""

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from flowspec_cli.security.models import Confidence, Finding, Location, Severity
from flowspec_cli.security.triage.engine import TriageEngine


@dataclass
class ConfusionMatrix:
    """Confusion matrix for classification evaluation."""

    tp_as_tp: int = 0  # Correctly classified True Positives
    tp_as_fp: int = 0  # True Positives misclassified as False Positives
    tp_as_ni: int = 0  # True Positives misclassified as Needs Investigation
    fp_as_tp: int = 0  # False Positives misclassified as True Positives
    fp_as_fp: int = 0  # Correctly classified False Positives
    fp_as_ni: int = 0  # False Positives misclassified as Needs Investigation
    ni_as_tp: int = 0  # Needs Investigation misclassified as True Positives
    ni_as_fp: int = 0  # Needs Investigation misclassified as False Positives
    ni_as_ni: int = 0  # Correctly classified Needs Investigation

    @property
    def total(self) -> int:
        """Total number of predictions."""
        return (
            self.tp_as_tp
            + self.tp_as_fp
            + self.tp_as_ni
            + self.fp_as_tp
            + self.fp_as_fp
            + self.fp_as_ni
            + self.ni_as_tp
            + self.ni_as_fp
            + self.ni_as_ni
        )

    @property
    def correct(self) -> int:
        """Number of correct predictions."""
        return self.tp_as_tp + self.fp_as_fp + self.ni_as_ni

    @property
    def accuracy(self) -> float:
        """Overall accuracy (correct / total)."""
        return self.correct / self.total if self.total > 0 else 0.0

    def update(self, ground_truth: str, predicted: str) -> None:
        """Update confusion matrix with a prediction.

        Args:
            ground_truth: Actual classification (TP/FP/NI)
            predicted: Predicted classification (TP/FP/NI)
        """
        mapping = {
            ("TP", "TP"): "tp_as_tp",
            ("TP", "FP"): "tp_as_fp",
            ("TP", "NI"): "tp_as_ni",
            ("FP", "TP"): "fp_as_tp",
            ("FP", "FP"): "fp_as_fp",
            ("FP", "NI"): "fp_as_ni",
            ("NI", "TP"): "ni_as_tp",
            ("NI", "FP"): "ni_as_fp",
            ("NI", "NI"): "ni_as_ni",
        }
        attr = mapping.get((ground_truth, predicted))
        if attr:
            setattr(self, attr, getattr(self, attr) + 1)


@dataclass
class BenchmarkMetrics:
    """Metrics for a specific classification category."""

    true_positives: int = 0  # Correctly predicted positive
    false_positives: int = 0  # Incorrectly predicted positive
    false_negatives: int = 0  # Incorrectly predicted negative
    true_negatives: int = 0  # Correctly predicted negative

    @property
    def precision(self) -> float:
        """Precision: TP / (TP + FP)."""
        denom = self.true_positives + self.false_positives
        return self.true_positives / denom if denom > 0 else 0.0

    @property
    def recall(self) -> float:
        """Recall: TP / (TP + FN)."""
        denom = self.true_positives + self.false_negatives
        return self.true_positives / denom if denom > 0 else 0.0

    @property
    def f1_score(self) -> float:
        """F1 Score: 2 * (precision * recall) / (precision + recall)."""
        p = self.precision
        r = self.recall
        return 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0


@dataclass
class Failure:
    """Record of a classification failure."""

    finding_id: str
    cwe_id: str
    ground_truth: str
    predicted: str
    confidence: float
    reasoning: str
    code_snippet: str


@dataclass
class BenchmarkResult:
    """Complete benchmark results."""

    total: int
    correct: int
    accuracy: float
    confusion_matrix: ConfusionMatrix
    per_cwe_accuracy: dict[str, float] = field(default_factory=dict)
    per_cwe_confusion: dict[str, ConfusionMatrix] = field(default_factory=dict)
    tp_metrics: BenchmarkMetrics = field(default_factory=BenchmarkMetrics)
    fp_metrics: BenchmarkMetrics = field(default_factory=BenchmarkMetrics)
    failures: list[Failure] = field(default_factory=list)


def load_benchmark_dataset(path: Path) -> tuple[dict[str, Any], list[dict]]:
    """Load benchmark dataset from JSON file.

    Args:
        path: Path to ground_truth.json

    Returns:
        Tuple of (metadata, findings list)
    """
    with open(path) as f:
        data = json.load(f)

    return data["metadata"], data["findings"]


def convert_to_finding(item: dict) -> Finding:
    """Convert benchmark dataset item to Finding object.

    Args:
        item: Dictionary from ground_truth.json

    Returns:
        Finding object for triage engine
    """
    return Finding(
        id=item["id"],
        scanner=item["scanner"],
        severity=Severity(item["severity"]),
        title=item["title"],
        description=item["description"],
        location=Location(
            file=Path(item["file"]),
            line_start=item["line_start"],
            line_end=item["line_end"],
            code_snippet=item["code_snippet"],
        ),
        cwe_id=item.get("cwe_id"),
        confidence=Confidence.MEDIUM,
    )


def run_benchmark(dataset: list[dict], llm_client: Any = None) -> BenchmarkResult:
    """Run benchmark on dataset and calculate metrics.

    Args:
        dataset: List of benchmark findings
        llm_client: Optional LLM client for AI-powered classification

    Returns:
        BenchmarkResult with accuracy metrics and failure analysis
    """
    engine = TriageEngine(llm_client=llm_client)
    confusion = ConfusionMatrix()
    per_cwe_confusion: dict[str, ConfusionMatrix] = defaultdict(ConfusionMatrix)
    failures: list[Failure] = []

    # Track TP/FP metrics (treating NI as negative for these metrics)
    tp_metrics = BenchmarkMetrics()
    fp_metrics = BenchmarkMetrics()

    print(f"Running benchmark on {len(dataset)} findings...")

    for i, item in enumerate(dataset, 1):
        if i % 10 == 0:
            print(f"  Processed {i}/{len(dataset)} findings...")

        finding = convert_to_finding(item)
        ground_truth = item["ground_truth"]["classification"]
        cwe_id = item.get("cwe_id", "unknown")

        # Run triage
        result = engine._triage_single(finding)
        predicted = result.classification.value

        # Update confusion matrices
        confusion.update(ground_truth, predicted)
        per_cwe_confusion[cwe_id].update(ground_truth, predicted)

        # Update TP metrics (binary: is it a true positive?)
        if ground_truth == "TP":
            if predicted == "TP":
                tp_metrics.true_positives += 1
            else:
                tp_metrics.false_negatives += 1
        else:
            if predicted == "TP":
                tp_metrics.false_positives += 1
            else:
                tp_metrics.true_negatives += 1

        # Update FP metrics (binary: is it a false positive?)
        if ground_truth == "FP":
            if predicted == "FP":
                fp_metrics.true_positives += 1
            else:
                fp_metrics.false_negatives += 1
        else:
            if predicted == "FP":
                fp_metrics.false_positives += 1
            else:
                fp_metrics.true_negatives += 1

        # Record failures
        if ground_truth != predicted:
            failures.append(
                Failure(
                    finding_id=item["id"],
                    cwe_id=cwe_id,
                    ground_truth=ground_truth,
                    predicted=predicted,
                    confidence=result.confidence,
                    reasoning=result.ai_reasoning,
                    code_snippet=item["code_snippet"],
                )
            )

    # Calculate per-CWE accuracy
    per_cwe_accuracy = {cwe: cm.accuracy for cwe, cm in per_cwe_confusion.items()}

    return BenchmarkResult(
        total=confusion.total,
        correct=confusion.correct,
        accuracy=confusion.accuracy,
        confusion_matrix=confusion,
        per_cwe_accuracy=per_cwe_accuracy,
        per_cwe_confusion=dict(per_cwe_confusion),
        tp_metrics=tp_metrics,
        fp_metrics=fp_metrics,
        failures=failures,
    )


def generate_report(
    result: BenchmarkResult, metadata: dict[str, Any], output_path: Path
) -> None:
    """Generate markdown benchmark report.

    Args:
        result: Benchmark results
        metadata: Dataset metadata
        output_path: Path to write report
    """
    report = f"""# AI Triage Engine Benchmark Report

**Date**: {metadata.get("created", "Unknown")}
**Dataset Version**: {metadata.get("version", "Unknown")}
**Total Findings**: {result.total}

## Executive Summary

- **Overall Accuracy**: {result.accuracy:.2%} ({result.correct}/{result.total} correct)
- **Target**: 85% accuracy
- **Status**: {"✓ PASS" if result.accuracy >= 0.85 else "✗ FAIL"}

### Quick Metrics

| Metric | Value |
|--------|-------|
| Accuracy | {result.accuracy:.2%} |
| TP Precision | {result.tp_metrics.precision:.2%} |
| TP Recall | {result.tp_metrics.recall:.2%} |
| TP F1 Score | {result.tp_metrics.f1_score:.2%} |
| FP Precision | {result.fp_metrics.precision:.2%} |
| FP Recall | {result.fp_metrics.recall:.2%} |
| FP F1 Score | {result.fp_metrics.f1_score:.2%} |

## Per-Classifier Accuracy

| CWE | Description | Accuracy | Correct/Total |
|-----|-------------|----------|---------------|
"""

    # Add per-CWE rows
    cwe_names = {
        "CWE-89": "SQL Injection",
        "CWE-79": "Cross-Site Scripting",
        "CWE-22": "Path Traversal",
        "CWE-798": "Hardcoded Secrets",
        "CWE-327": "Weak Cryptography",
    }

    for cwe_id in sorted(result.per_cwe_accuracy.keys()):
        accuracy = result.per_cwe_accuracy[cwe_id]
        cm = result.per_cwe_confusion[cwe_id]
        name = cwe_names.get(cwe_id, cwe_id)
        status = "✓" if accuracy >= 0.85 else "✗"
        report += f"| {cwe_id} | {name} | {status} {accuracy:.2%} | {cm.correct}/{cm.total} |\n"

    # Confusion Matrix
    cm = result.confusion_matrix
    report += f"""
## Confusion Matrix

|  | Predicted TP | Predicted FP | Predicted NI |
|---|--------------|--------------|--------------|
| **Actual TP** | {cm.tp_as_tp} ✓ | {cm.tp_as_fp} ✗ | {cm.tp_as_ni} ~ |
| **Actual FP** | {cm.fp_as_tp} ✗ | {cm.fp_as_fp} ✓ | {cm.fp_as_ni} ~ |
| **Actual NI** | {cm.ni_as_tp} ~ | {cm.ni_as_fp} ~ | {cm.ni_as_ni} ✓ |

Legend:
- ✓ Correct classification
- ✗ Incorrect classification
- ~ Partial credit (NI is uncertain)

## Detailed Metrics

### True Positive Detection

| Metric | Value | Description |
|--------|-------|-------------|
| Precision | {result.tp_metrics.precision:.2%} | Of predicted TPs, how many are actually TP? |
| Recall | {result.tp_metrics.recall:.2%} | Of actual TPs, how many did we find? |
| F1 Score | {result.tp_metrics.f1_score:.2%} | Harmonic mean of precision and recall |

- True Positives: {result.tp_metrics.true_positives} (correctly identified vulnerabilities)
- False Positives: {result.tp_metrics.false_positives} (incorrectly flagged safe code)
- False Negatives: {result.tp_metrics.false_negatives} (missed real vulnerabilities) ⚠️
- True Negatives: {result.tp_metrics.true_negatives} (correctly identified safe code)

### False Positive Detection

| Metric | Value | Description |
|--------|-------|-------------|
| Precision | {result.fp_metrics.precision:.2%} | Of predicted FPs, how many are actually FP? |
| Recall | {result.fp_metrics.recall:.2%} | Of actual FPs, how many did we catch? |
| F1 Score | {result.fp_metrics.f1_score:.2%} | Harmonic mean of precision and recall |

## Failure Analysis

**Total Failures**: {len(result.failures)} ({len(result.failures) / result.total:.1%})

### Failure Breakdown by Type

"""

    # Group failures by type
    failure_types: dict[str, list[Failure]] = defaultdict(list)
    for failure in result.failures:
        key = f"{failure.ground_truth} → {failure.predicted}"
        failure_types[key].append(failure)

    for failure_type, failures in sorted(
        failure_types.items(), key=lambda x: len(x[1]), reverse=True
    ):
        report += f"\n#### {failure_type} ({len(failures)} failures)\n\n"

        # Show up to 5 examples per type
        for failure in failures[:5]:
            report += f"""
**{failure.finding_id}** ({failure.cwe_id})

- Ground Truth: {failure.ground_truth}
- Predicted: {failure.predicted}
- Confidence: {failure.confidence:.0%}
- Code: `{failure.code_snippet[:100]}{"..." if len(failure.code_snippet) > 100 else ""}`
- Reasoning: {failure.reasoning[:200]}{"..." if len(failure.reasoning) > 200 else ""}

"""

        if len(failures) > 5:
            report += f"\n_... and {len(failures) - 5} more similar failures_\n"

    # Recommendations
    report += """
## Recommendations

"""

    if result.accuracy < 0.85:
        report += f"""
### CRITICAL: Accuracy Below Target ({result.accuracy:.2%} < 85%)

Priority improvements needed:

"""
        # Identify weakest classifiers
        weak_cwes = [
            (cwe, acc) for cwe, acc in result.per_cwe_accuracy.items() if acc < 0.85
        ]
        weak_cwes.sort(key=lambda x: x[1])

        for cwe, acc in weak_cwes:
            name = cwe_names.get(cwe, cwe)
            report += f"1. **{cwe} ({name})**: {acc:.2%} accuracy\n"
            report += "   - Review classifier heuristics\n"
            report += "   - Add more training examples\n"
            report += "   - Improve LLM prompt\n\n"

        # Analyze failure patterns
        if cm.tp_as_fp > 0:
            report += f"\n2. **False Negative Risk**: {cm.tp_as_fp} real vulnerabilities classified as FP\n"
            report += "   - Review conservative thresholds\n"
            report += "   - Add patterns for missed vulnerability types\n\n"

        if cm.fp_as_tp > 0:
            report += f"\n3. **False Positive Risk**: {cm.fp_as_tp} safe patterns classified as TP\n"
            report += "   - Add detection for safe patterns\n"
            report += "   - Improve sanitization recognition\n\n"

    else:
        report += """
### SUCCESS: Target Accuracy Achieved ✓

The triage engine meets the 85% accuracy target. Continue monitoring:

1. **Per-Classifier Performance**: Ensure all CWEs maintain >80% accuracy
2. **False Negative Rate**: Monitor missed vulnerabilities
3. **Confidence Calibration**: Verify confidence scores align with accuracy
4. **Edge Case Coverage**: Add more complex examples to dataset

"""

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)

    print(f"\nReport written to: {output_path}")


def main() -> int:
    """Main entry point for benchmark script."""
    parser = argparse.ArgumentParser(description="Benchmark AI triage engine accuracy")
    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="Path to ground_truth.json dataset",
    )
    parser.add_argument(
        "--report",
        type=Path,
        required=True,
        help="Path to write markdown report",
    )
    parser.add_argument(
        "--llm",
        action="store_true",
        help="Use LLM-powered classification (requires API key)",
    )

    args = parser.parse_args()

    # Validate dataset exists
    if not args.dataset.exists():
        print(f"Error: Dataset not found: {args.dataset}", file=sys.stderr)
        return 1

    # Load dataset
    print(f"Loading dataset from {args.dataset}...")
    metadata, findings = load_benchmark_dataset(args.dataset)
    print(f"  Loaded {len(findings)} findings")

    # Run benchmark
    llm_client = None  # TODO: Add LLM client if --llm flag set
    if args.llm:
        print("Warning: LLM mode not yet implemented, using heuristics only")

    result = run_benchmark(findings, llm_client)

    # Generate report
    print("\nGenerating report...")
    generate_report(result, metadata, args.report)

    # Print summary
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"Overall Accuracy: {result.accuracy:.2%} ({result.correct}/{result.total})")
    print("Target: 85%")
    print(f"Status: {'✓ PASS' if result.accuracy >= 0.85 else '✗ FAIL'}")
    print("\nPer-Classifier Accuracy:")
    for cwe_id in sorted(result.per_cwe_accuracy.keys()):
        accuracy = result.per_cwe_accuracy[cwe_id]
        status = "✓" if accuracy >= 0.85 else "✗"
        print(f"  {status} {cwe_id}: {accuracy:.2%}")
    print("=" * 70)

    return 0 if result.accuracy >= 0.85 else 1


if __name__ == "__main__":
    sys.exit(main())
