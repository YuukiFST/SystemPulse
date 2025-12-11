import subprocess
import json
from typing import Callable, Optional, Dict, Any, List


class CommandRunner:
    @staticmethod
    def run_powershell(
        script: str,
        timeout: int = 30
    ) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
    
    @staticmethod
    def run_powershell_json(
        script: str,
        timeout: int = 30
    ) -> Optional[List[Dict[str, Any]]]:
        result = CommandRunner.run_powershell(script, timeout)
        if not result.stdout.strip():
            return []
        data = json.loads(result.stdout.strip())
        if isinstance(data, dict):
            return [data]
        return data
    
    @staticmethod
    def run_shell_streaming(
        command: str,
        on_output: Callable[[str], None],
        on_complete: Optional[Callable[[int], None]] = None
    ) -> subprocess.Popen:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
            shell=True
        )
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                on_output(output.strip())
        
        if on_complete:
            on_complete(process.returncode)
        
        return process
    
    @staticmethod
    def run_shell(command: str, timeout: int = 30) -> subprocess.CompletedProcess:
        return subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
