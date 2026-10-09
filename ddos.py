import argparse
import concurrent.futures
import json
import time
import urllib.request
import urllib.error


def make_request(url, timeout, method, data=None, token=None):
    start = time.perf_counter()

    try:
        headers = {}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        if method == "POST":
            headers["Content-Type"] = "application/json"

        body = None

        if method == "POST" and data:
            body = data.encode("utf-8")

        request = urllib.request.Request(
            url,
            data=body,
            headers=headers,
            method=method
        )

        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read()
            elapsed = time.perf_counter() - start
            return response.status, elapsed

    except urllib.error.HTTPError as error:
        elapsed = time.perf_counter() - start
        return error.code, elapsed

    except Exception:
        elapsed = time.perf_counter() - start
        return "ERROR", elapsed


def main():
    parser = argparse.ArgumentParser(
        description="Controlled load testing tool for local services."
    )

    parser.add_argument(
        "host",
        help="Host to test, for example 127.0.0.1"
    )

    parser.add_argument(
        "port",
        type=int,
        help="Port to test"
    )

    parser.add_argument(
        "--path",
        default="/",
        help="HTTP path to test"
    )

    parser.add_argument(
        "--method",
        choices=["GET", "POST"],
        default="GET",
        help="HTTP method"
    )

    parser.add_argument(
        "--data",
        help="JSON data for POST requests"
    )

    parser.add_argument(
        "--token",
        help="JWT token to send as Authorization: Bearer <token>"
    )

    parser.add_argument(
        "-n",
        "--requests",
        type=int,
        default=100,
        help="Total number of requests"
    )

    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=10,
        help="Maximum number of simultaneous requests"
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=5,
        help="Maximum timeout per request"
    )

    args = parser.parse_args()

    if args.requests <= 0:
        raise ValueError("The number of requests must be greater than 0.")

    if args.concurrency <= 0:
        raise ValueError("Concurrency must be greater than 0.")

    if args.concurrency > args.requests:
        args.concurrency = args.requests

    data = None

    if args.method == "POST" and args.data:
        try:
            json.loads(args.data)
        except json.JSONDecodeError:
            raise ValueError("The --data value must contain valid JSON.")

        data = args.data

    url = f"http://{args.host}:{args.port}{args.path}"

    print("=" * 60)
    print("CONTROLLED LOAD TEST")
    print("=" * 60)
    print(f"URL:          {url}")
    print(f"Method:       {args.method}")
    print(f"Requests:     {args.requests}")
    print(f"Concurrency:  {args.concurrency}")
    print(f"Timeout:      {args.timeout}s")

    if data:
        print("JSON data:    [configured]")

    if args.token:
        print("JWT:          [configured]")

    print("=" * 60)

    start_total = time.perf_counter()

    results = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.concurrency
    ) as executor:

        futures = [
            executor.submit(
                make_request,
                url,
                args.timeout,
                args.method,
                data,
                args.token
            )
            for _ in range(args.requests)
        ]

        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    total_time = time.perf_counter() - start_total

    success = sum(
        1 for status, _ in results
        if isinstance(status, int) and 200 <= status < 300
    )

    http_errors = sum(
        1 for status, _ in results
        if isinstance(status, int) and status >= 400
    )

    errors = sum(
        1 for status, _ in results
        if status == "ERROR"
    )

    valid_times = [
        elapsed
        for _, elapsed in results
    ]

    average = (
        sum(valid_times) / len(valid_times)
        if valid_times
        else 0
    )

    rps = (
        args.requests / total_time
        if total_time > 0
        else 0
    )

    print()
    print("RESULTS")
    print("-" * 60)
    print(f"Completed requests     : {len(results)}")
    print(f"HTTP 2xx               : {success}")
    print(f"HTTP 4xx/5xx           : {http_errors}")
    print(f"Connection errors      : {errors}")
    print(f"Total time             : {total_time:.2f} s")
    print(f"Average response time  : {average:.4f} s")
    print(f"Requests per second    : {rps:.2f}")
    print("-" * 60)


if __name__ == "__main__":
    main()