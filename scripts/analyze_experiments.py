from collections import defaultdict
from pathlib import Path

import json
import statistics


REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = REPO_ROOT / "results.jsonl"
OUTPUT_FILE = REPO_ROOT / "latency_results.jsonl"

# Require at least this many chain lengths before accepting a result.
MIN_FIT_POINTS = 5

# Maximum error, in cycles, that an integer-latency model may have.
RESIDUAL_TOLERANCE = 3.0

# Just a generous upper bound for instruction latency.
MAX_LATENCY = 256


def linear_regression_slope(points):
    """
    Ordinary least-squares slope.

    Used only as a diagnostic. The reported latency is obtained from
    the integer-latency model below.
    """
    xs = [n for n, cycles in points]
    ys = [cycles for n, cycles in points]

    x_mean = statistics.mean(xs)
    y_mean = statistics.mean(ys)

    numerator = sum(
        (x - x_mean) * (y - y_mean)
        for x, y in zip(xs, ys)
    )

    denominator = sum(
        (x - x_mean) ** 2
        for x in xs
    )

    if denominator == 0:
        return None

    return numerator / denominator


def calculate_local_slopes(points):
    """
    Calculate:

        delta_cycles / delta_n

    between consecutive chain lengths.
    """
    slopes = []

    for (n1, c1), (n2, c2) in zip(points, points[1:]):
        slope = (c2 - c1) / (n2 - n1)

        slopes.append({
            "from_n": n1,
            "to_n": n2,
            "slope": slope,
        })

    return slopes


def fit_integer_latency(points):
    """
    Fit:

        cycles = overhead + latency * n

    while requiring latency to be an integer.

    For a given latency candidate, the implied overhead at every
    measurement is:

        overhead_i = cycles_i - latency * n_i

    If the candidate is correct, these values should all be nearly
    identical.
    """

    best = None

    for latency in range(1, MAX_LATENCY + 1):

        implied_overheads = [
            cycles - latency * n
            for n, cycles in points
        ]

        overhead = statistics.median(implied_overheads)

        residuals = [
            cycles - (overhead + latency * n)
            for n, cycles in points
        ]

        abs_residuals = [abs(r) for r in residuals]

        result = {
            "latency": latency,
            "overhead": overhead,
            "max_abs_residual": max(abs_residuals),
            "mean_abs_residual": statistics.mean(abs_residuals),
            "residuals": residuals,
        }

        if best is None:
            best = result
            continue

        # Minimize worst error first, then average error.
        if (
            result["max_abs_residual"],
            result["mean_abs_residual"],
        ) < (
            best["max_abs_residual"],
            best["mean_abs_residual"],
        ):
            best = result

    return best


def analyze_experiment(records):
    """
    Find the longest prefix of n values that fits a clean integer
    latency model.
    """

    records = sorted(records, key=lambda x: x["n"])

    # Use minimum runtime as the primary microbenchmark measurement.
    points = [
        (record["n"], record["min_cycles"])
        for record in records
    ]

    local_slopes = calculate_local_slopes(points)

    #
    # Try the largest range first.
    #
    # If large generated programs start suffering from instruction
    # fetch/cache/front-end effects, progressively remove the largest n.
    #
    accepted_fit = None
    accepted_points = None

    for end in range(len(points), MIN_FIT_POINTS - 1, -1):

        candidate_points = points[:end]

        fit = fit_integer_latency(candidate_points)

        if fit["max_abs_residual"] <= RESIDUAL_TOLERANCE:
            accepted_fit = fit
            accepted_points = candidate_points
            break

    if accepted_fit is None:
        return {
            "latency_cycles": None,
            "status": "no_stable_integer_fit",
            "local_slopes": local_slopes,
        }

    continuous_slope = linear_regression_slope(accepted_points)

    latency = accepted_fit["latency"]

    #
    # Simple confidence classification.
    #
    slope_error = abs(continuous_slope - latency)

    if (
        len(accepted_points) >= 5
        and accepted_fit["max_abs_residual"] <= 1
        and slope_error <= 0.05
    ):
        confidence = "high"

    elif (
        accepted_fit["max_abs_residual"] <= RESIDUAL_TOLERANCE
        and slope_error <= 0.15
    ):
        confidence = "medium"

    else:
        confidence = "low"

    return {
        "latency_cycles": latency,
        "overhead_cycles": accepted_fit["overhead"],
        "continuous_slope": continuous_slope,
        "fit_n_min": accepted_points[0][0],
        "fit_n_max": accepted_points[-1][0],
        "fit_points": len(accepted_points),
        "max_abs_residual": accepted_fit["max_abs_residual"],
        "mean_abs_residual": accepted_fit["mean_abs_residual"],
        "confidence": confidence,
        "status": "ok",
        "local_slopes": local_slopes,
    }


def main():

    groups = defaultdict(list)

    #
    # Load and group measurements.
    #
    with INPUT_FILE.open() as f:
        for line in f:
            if not line.strip():
                continue

            record = json.loads(line)

            key = (
                record["encoding"],
                record["benchmark_type"],
                record["experiment"],
                record["instruction"],
            )

            groups[key].append(record)

    #
    # Analyze every experiment.
    #
    with OUTPUT_FILE.open("w") as output:

        for key, records in sorted(groups.items()):

            (
                encoding,
                benchmark_type,
                experiment,
                instruction,
            ) = key

            analysis = analyze_experiment(records)

            result = {
                "encoding": encoding,
                "benchmark_type": benchmark_type,
                "experiment": experiment,
                "instruction": instruction,
                **analysis,
            }

            output.write(json.dumps(result) + "\n")

            print()
            print(f"{instruction} : {experiment}")

            if analysis["latency_cycles"] is None:
                print("  Latency:    UNKNOWN")
                print("  Status:     no stable integer fit")

            else:
                print(
                    f"  Latency:    "
                    f"{analysis['latency_cycles']} cycles"
                )

                print(
                    f"  OLS slope:  "
                    f"{analysis['continuous_slope']:.4f}"
                )

                print(
                    f"  Overhead:   "
                    f"{analysis['overhead_cycles']:.2f} cycles"
                )

                print(
                    f"  Fit range:  "
                    f"n={analysis['fit_n_min']} "
                    f"through n={analysis['fit_n_max']}"
                )

                print(
                    f"  Residual:   "
                    f"{analysis['max_abs_residual']:.2f} cycles max"
                )

                print(
                    f"  Confidence: "
                    f"{analysis['confidence']}"
                )

            print("  Local slopes:")

            for slope in analysis["local_slopes"]:
                print(
                    f"    "
                    f"{slope['from_n']:>4} -> "
                    f"{slope['to_n']:<4}: "
                    f"{slope['slope']:.3f}"
                )


if __name__ == "__main__":
    main()
