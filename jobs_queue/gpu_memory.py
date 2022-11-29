import argparse
import json
import pprint
import time
from dataclasses import dataclass
from datetime import timedelta
from subprocess import check_output
from typing import Any, Dict, List, Union

from easydict import EasyDict as EDict

__all__ = [
    "GpuMemoryOutOfRange",
    "GpuManager",
    "wait_for_free_space",
]


class GpuMemoryOutOfRange(Exception):
    ...


class ReprClss(type):
    def __str__(cls) -> str:
        cls.update()
        return f"""{cls.__name__}(
    USED={cls.USED:,} MB, USED_by_device={dict(map(lambda x: (x[0], f"{x[1]:,} MB") , cls.USED_single.items()))}
    TOTAL={cls.TOTAL:,} MB, TOTAL_by_device={dict(map(lambda x: (x[0], f"{x[1]:,} MB") , cls.TOTAL_single.items()))}
    FREE={cls.FREE:,} MB, FREE_by_device={dict(map(lambda x: (x[0], f"{x[1]:,} MB") , cls.FREE_single.items()))}
)"""

    __repr__ = __str__


class GpuManager(metaclass=ReprClss):
    "Uses gpustats to get the graphical memory statistics"
    USED_single: Dict[int, int] = dict()
    USED: int = None
    TOTAL_single: Dict[int, int] = dict()
    TOTAL: int = None
    FREE_single: Dict[int, int] = dict()
    FREE: int = None

    def update():
        "Update Manager variables and return output of gpustat"
        out = EDict(json.loads(check_output(f"gpustat --json".split())))

        GpuManager.USED_single = {gpu.index: gpu["memory.used"] for gpu in out.gpus}
        GpuManager.TOTAL_single = {gpu.index: gpu["memory.total"] for gpu in out.gpus}
        GpuManager.FREE_single = {
            gpu.index: GpuManager.TOTAL_single[gpu.index]
            - GpuManager.USED_single[gpu.index]
            for gpu in out.gpus
        }

        GpuManager.USED = sum(GpuManager.USED_single.values())
        GpuManager.TOTAL = sum(GpuManager.TOTAL_single.values())
        GpuManager.FREE = sum(GpuManager.FREE_single.values())

        return out

    def single_gpu_available(gpu_mem: int) -> Union[int, bool]:
        "Return the gpu id that is being less used if free amount matches needed gpu_mem otherwise return False"
        GpuManager.update()

        free_dict = {
            gpu_id: gpu_mem < free for gpu_id, free in GpuManager.FREE_single.items()
        }  # gpu_id: is free or not

        free_dict = dict(filter(lambda v: v[1], free_dict.items()))  # Filter free ids
        sorted_free = sorted(
            free_dict, key=lambda x: GpuManager.FREE_single[x], reverse=True
        )  # Sort by less amount being used

        if sorted_free:  # If not empty return first item
            return sorted_free[0]

        return False  # Else return False

    def total_gpu_available(gpu_mem: int) -> bool:
        "Return True if the needed amount is available over all the gpus"
        GpuManager.update()

        return gpu_mem < GpuManager.FREE

    def manage_gpus(gpu_mem):
        GpuManager.update()
        if gpu_mem > GpuManager.TOTAL:
            raise GpuMemoryOutOfRange(
                f"Total gpu memory={GpuManager.TOTAL}. Requested gpu memory={gpu_mem}"
            )

        if any(
            gpu_mem <= single_gpu for single_gpu in GpuManager.TOTAL_single.values()
        ):
            # If needed gpu_mem requires only one gpu
            return GpuManager.single_gpu_available(gpu_mem)
        else:
            return GpuManager.total_gpu_available(gpu_mem)

    def get_running_processes() -> List[Dict[str, Any]]:
        def get_real_cmd(pid):
            return check_output(f"ps -p {pid} -o cmd=".split()).strip().decode()

        def get_running_time_secs(pid):
            return int(check_output(f"ps -p {pid} -o etimes=".split()).strip())

        @dataclass
        class Process:
            username: str
            command: str
            gpu_memory_usage: int
            pid: int
            gpu_id: int
            time_secs: int
            # Extras
            full_command: float
            cpu_memory_usage: float
            cpu_percent: float

            def __str__(self) -> str:
                cmd_size = 40
                cmd_extra = "[...]" if len(self.command) > cmd_size else ""
                return f"{self.__class__.__name__}( username={self.username}, command={self.command[:cmd_size]}{cmd_extra}, gpu_memory_usage={self.gpu_memory_usage:,} MB, pid={self.pid}, gpu_id={self.gpu_id}, time_secs={timedelta(seconds=self.time_secs)} )"

            __repr__ = __str__

        out = GpuManager.update()

        processes = []
        for gpu in out.gpus:
            for process in gpu.processes:
                process.update(
                    gpu_id=gpu.index,
                    command=get_real_cmd(process.pid),
                    time_secs=get_running_time_secs(process.pid),
                )

            processes.extend([Process(**p) for p in gpu.processes])

        return processes


def wait_for_free_space(gpu_mem, sleep_time_secs: int = 1, verbose: bool = False):
    start = time.perf_counter_ns()
    while 1:
        free = GpuManager.manage_gpus(gpu_mem)

        if free is not False:
            if verbose:
                print()
            return free

        time.sleep(sleep_time_secs)

        if verbose:
            print(
                f"Time slept: {timedelta(seconds=round((time.perf_counter_ns()-start)/1e9))}",
                end="\r",
            )


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gpu_mem", default=0, type=float, help="GPU space needed to run cmd"
    )

    return parser


if __name__ == "__main__":
    print(GpuManager)
    pprint.pprint(GpuManager.get_running_processes())

    # args = get_parser().parse_args()
    # print(args)
    # print(cmd)

    # now_free = wait_for_free_space(args.gpu_mem, verbose=True)
    # print(now_free)
