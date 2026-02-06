import argparse

from src.potentiostat_protocol.executor import DryRunBackend, PotentiostatExecutor
from src.potentiostat_protocol.gamry_backend import GamryBackend
from src.potentiostat_protocol.schema import PotentiostatExperiment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run potentiostat experiment YAML")
    parser.add_argument("experiment_file", type=str, help="Path to YAML experiment file")
    parser.add_argument(
        "--backend",
        type=str,
        choices=["dry-run", "gamry"],
        default="dry-run",
        help="Execution backend. Use 'gamry' for real hardware runs.",
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Repository root used to locate the local pygamry project for gamry backend.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    experiment = PotentiostatExperiment.from_yaml(args.experiment_file)

    if args.backend == "gamry":
        backend = GamryBackend(repo_root=args.repo_root)
    else:
        backend = DryRunBackend()

    executor = PotentiostatExecutor(backend)
    executor.execute(experiment)

    if args.backend == "dry-run":
        print("Dry-run operations:")
        for item in backend.records:
            print(item)


if __name__ == "__main__":
    main()
