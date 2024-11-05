import multiprocessing
import pickle
from typing import Any, Callable, Optional


class SubprocessRunner:
    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.manager = multiprocessing.Manager()

    def run(self, timeout: Optional[int] = None) -> Any:
        return_dict = self.manager.dict()

        def worker(return_dict, *args, **kwargs):
            try:
                result = self.func(*args, **kwargs)
                return_dict["result"] = result
            except Exception as e:
                # Serialize the exception
                return_dict["error"] = pickle.dumps(e)

        process = multiprocessing.Process(
            target=worker, args=(return_dict,) + self.args, kwargs=self.kwargs
        )
        process.start()

        # Join with timeout
        process.join(timeout)

        if process.is_alive():  # Check if the process is still running
            process.kill()  # Force kill the process
            process.join(timeout)  # Ensure the process has finished
            raise TimeoutError(f"Process timed out after {timeout} seconds")

        if process.exitcode != 0:
            raise RuntimeError(f"Process crashed with exit code: {process.exitcode}")

        # Check for errors in the return_dict
        if "error" in return_dict:
            # Deserialize the exception
            error = pickle.loads(return_dict["error"])
            raise error  # Re-raise the original exception

        return return_dict.get("result")
