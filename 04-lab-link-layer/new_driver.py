#!/usr/bin/env python3
"""Run the lab scenarios using packet identities instead of arrival windows.

Temporary host instrumentation assigns ICMP identifiers without changing the
MAC addresses, send schedule, or switch under test. Requires Cougarnet, just
like driver.py. Run with python3 new_driver.py.
"""

from collections import Counter
import argparse
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile

import driver


LAB_DIR = Path(__file__).resolve().parent
EVENTS = [
    (1, 1, 'a', 'c'), (3, 1, 'c', 'a'),
    (1, 2, 'a', 'c'), (1, 3, 'a', 'broadcast'),
    (5, 1, 'e', 'a'), (1, 4, 'a', 'e'),
    (3, 2, 'e', 'a'), (1, 5, 'a', 'e'),
    (5, 2, 'e', 'a'), (1, 6, 'a', 'c'),
]
FRAME_RE = re.compile(
    driver.LOG_PREFIX + r'FRAME id=(?P<id>\d+) seq=(?P<seq>\d+) '
    r'src=(?P<src>\S+) dst=(?P<dst>\S+)$')

# This wrapper runs only in temporary scenario copies. Both spoofed sends from
# c and real sends from e retain their original Ethernet source addresses.
HOST_WRAPPER = '''#!/usr/bin/python3
import socket
import sys
sys.path.insert(0, {lab_dir!r})
import host

original_send = host.Host.send_icmp_echo
send_count = 0

def send(self, src, dst, srcmac, dstmac, id, seq):
    global send_count
    send_count += 1
    sender_id = ord(socket.gethostname()) - ord('a') + 1
    original_send(self, src, dst, srcmac, dstmac, sender_id, send_count)

def receive(self, frame, intf):
    packet = host.Ether(frame)
    if host.ICMP not in packet:
        self.log('UNEXPECTED_FRAME')
        return
    icmp = packet[host.ICMP]
    self.log(f'FRAME id={{icmp.id}} seq={{icmp.seq}} '
             f'src={{packet.src}} dst={{packet.dst}}')

host.Host.send_icmp_echo = send
host.Host._handle_frame = receive
host.main()
'''


def mac(name):
    return ('ff:ff:ff:ff:ff:ff' if name == 'broadcast'
            else '00:00:00:' + ':'.join([name * 2] * 3))


class IdentityTester:
    def evaluate_lines(self, lines):
        observations = {event[:2]: [] for event in EVENTS}
        times = {}
        unexpected = []
        started = stopped = False
        for line in lines:
            started |= driver.LOG_START_RE.search(line) is not None
            stopped |= driver.LOG_STOP_RE.search(line) is not None
            match = FRAME_RE.search(line)
            if match is None:
                if 'UNEXPECTED_FRAME' in line or ' FRAME ' in line:
                    unexpected.append(line)
                continue
            key = (int(match['id']), int(match['seq']))
            if key not in observations:
                unexpected.append(line)
                continue
            observations[key].append((match['hostname'], match['src'], match['dst']))
            times.setdefault(key, float(match['time']))

        solutions = [item for item in self.expected_observations if item is not None]
        success = 0
        for event, solution in zip(EVENTS, solutions):
            sender, sequence, source, destination = event
            key = (sender, sequence)
            expected_hosts = solution[0][1]
            expected = Counter((name, mac(source), mac(destination))
                               for name in expected_hosts)
            actual = Counter(observations[key])
            if actual == expected:
                success += 1
                continue
            seen = ', '.join(sorted(item[0] for item in observations[key]))
            sys.stderr.write(
                f'ERROR: Time {times.get(key, 0):0.3f}: Expected FRAME at '
                f'{", ".join(sorted(expected_hosts))}, but observed FRAME at {seen}'
                f' (id={sender}, seq={sequence}; MAC addresses also checked)\n')

        # Never report a perfect run when unexpected traffic or an incomplete
        # simulation is present, even if all expected deliveries also occurred.
        for line in unexpected:
            sys.stderr.write(f'ERROR: Unexpected frame: {line}\n')
        if not started or not stopped:
            sys.stderr.write('ERROR: Missing START or STOP; simulation incomplete\n')
        if unexpected or not started or not stopped:
            success = min(success, len(EVENTS) - 1)
        return success, len(EVENTS)

    def run(self, verbose=False):
        with tempfile.TemporaryDirectory(prefix='link-layer-') as directory:
            wrapper = Path(directory) / 'host.py'
            wrapper.write_text(HOST_WRAPPER.format(lab_dir=str(LAB_DIR)))
            wrapper.chmod(0o755)
            config = Path(directory) / self.cmd[-1]
            config.write_text((LAB_DIR / self.cmd[-1]).read_text().replace(
                'prog=./host.py', f'prog={wrapper.as_posix()}').replace(
                'prog=./switch.py', f'prog={(LAB_DIR / "switch.py").as_posix()}'))
            command = self.cmd[:-1] + [str(config)]
            process = subprocess.Popen(command, cwd=LAB_DIR,
                                       stdout=subprocess.PIPE, text=True,
                                       env={**os.environ, 'PYTHONUNBUFFERED': '1'})
            try:
                if verbose:
                    lines = []
                    for line in process.stdout:
                        print(line, end='', flush=True)
                        lines.append(line)
                    process.stdout.close()
                    process.wait()
                    output = ''.join(lines)
                else:
                    output, _ = process.communicate()
            except KeyboardInterrupt:
                process.send_signal(signal.SIGINT)
                process.communicate()
                raise
            if process.returncode:
                sys.stderr.write(f'ERROR: Cougarnet exited with {process.returncode}\n')
                return 0, len(EVENTS)
            return self.evaluate_lines(output.splitlines())


class Scenario1(IdentityTester, driver.Scenario1):
    pass


class Scenario2(IdentityTester, driver.Scenario2):
    pass


class Scenario3(IdentityTester, driver.Scenario3):
    pass


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='show live Cougarnet output before grading results')
    selection = parser.add_mutually_exclusive_group()
    for number in (1, 2, 3):
        selection.add_argument(f'-{number}', dest='scenario',
                               action='store_const', const=number,
                               help=f'run only Scenario{number}')
    args = parser.parse_args(argv)
    scenarios = (Scenario1, Scenario2, Scenario3)
    if args.scenario is not None:
        scenarios = (scenarios[args.scenario - 1],)
    try:
        for scenario in scenarios:
            print(f'Running {scenario.__name__}...', flush=True)
            success, total = scenario().run(verbose=args.verbose)
            sys.stderr.write(f'  Result: {success}/{total}\n')
    except KeyboardInterrupt:
        sys.stderr.write('Interrupted\n')
    except OSError as error:
        sys.stderr.write(f'ERROR: {error}\n')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
