#!/usr/bin/env python
import argparse
import random
import subprocess

import xmltodict


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Find indices of free GPUs on system",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-f",
        "--print-only-first",
        action="store_true",
        help="Print only first available index",
    )
    parser.add_argument(
        "-r", "--randomize", action="store_true", help="Randomize order of indices"
    )
    parser.add_argument(
        "-w", "--who", action="store_true", help="Print GPUs used by each user"
    )
    parser.add_argument(
        "-m",
        "--sort-by-memory",
        action="store_true",
        help="Sort GPUs by amount of free memory. Without this, only completely empty GPUs will be printed",
    )
    args = parser.parse_args()
    return args


def _enum_gpus():
    stdout = subprocess.check_output(("nvidia-smi", "-q", "-x"))
    X = xmltodict.parse(stdout)

    idxs = []
    for idx, gpu in enumerate(X["nvidia_smi_log"]["gpu"]):
        yield (idx, gpu)


def find_free_gpus():
    idxs = [idx for idx, gpu in _enum_gpus() if gpu["processes"] is None]
    return idxs


def resolve_gpu_users():
    from collections import defaultdict

    import psutil

    gpu_users = defaultdict(set)

    for idx, gpu in _enum_gpus():
        if gpu["processes"] is None:
            continue
        pi = gpu["processes"]["process_info"]
        if not isinstance(pi, list):
            pi = [pi]
        pids = [int(P["pid"]) for P in pi]
        for pid in pids:
            user = psutil.Process(pid).username()
            gpu_users[user].add(idx)

    return dict(gpu_users)


def sort_gpus_by_free_memory():
    free_mem = {}
    total_mem = {}
    for idx, gpu in _enum_gpus():
        suffix = " MiB"
        free = gpu["fb_memory_usage"]["free"]
        total = gpu["fb_memory_usage"]["total"]
        assert free.endswith(suffix) and total.endswith(suffix)
        free_mem[idx] = 2**20 * int(free[: -len(suffix)])
        total_mem[idx] = 2**20 * int(total[: -len(suffix)])

    sorted_gpus = sorted(free_mem.keys(), key=lambda idx: -free_mem[idx])
    return sorted_gpus


def main():
    args = _parse_args()

    if args.who:
        gpu_users = resolve_gpu_users()
        for user in sorted(gpu_users.keys()):
            print(user, ",".join([str(idx) for idx in sorted(gpu_users[user])]))
        return

    elif args.sort_by_memory:
        # Find GPU with most free memory.
        gpus = sort_gpus_by_free_memory()
        print(gpus[0])
        return

    else:
        # Show only entirely free GPUs.
        gpus = find_free_gpus()
        if args.randomize:
            random.shuffle(gpus)
        if args.print_only_first:
            print(gpus[0] if len(gpus) > 0 else "")
        else:
            print(" ".join([str(idx) for idx in gpus]))


if __name__ == "__main__":
    main()
