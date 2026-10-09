# ELF Load Testing

Controlled load testing tool developed to evaluate the behavior of the e.l.f. application services under different levels of HTTP request load.

This project was developed as part of a Docker security and load testing practice.

---

## Objective

The objective of this project is to perform controlled HTTP load tests against the e.l.f. application services and identify the highest stable load reached by each service.

The tests were performed against three local Docker services:

- Frontend: port 5173
- Backend: port 3000
- LDAP HTTP service: port 3001

The LDAP service also uses TLS on port 636.

The load testing script was executed outside the Docker containers.

---

## Technologies

- Python 3
- Docker
- Docker Desktop
- Nginx
- Node.js
- Express
- JWT
- LDAP
- Fail2Ban
- Windows
- WSL 2

---

## Project Structure

```text
elf-load-testing/
├── ddos.py
└── README.md
```

The `ddos.py` file contains the controlled HTTP load testing script.

---

## DDoS Script Modification

The original DDoS/load testing script was modified so that the target host and port could be provided as command-line arguments.

The script was also modified to support:

- HTTP path
- HTTP method
- JSON data
- JWT authentication
- Total number of requests
- Concurrent requests
- Request timeout

This allows the same script to test different services without changing the source code.

The script was kept outside the three Docker images, as required by the practice.

---

## Command-Line Usage

The basic command structure is:

```text
py -3 ddos.py HOST PORT
```

Example:

```text
py -3 ddos.py 127.0.0.1 5173
```

The available options can be viewed with:

```text
py -3 ddos.py --help
```

---

## Command-Line Arguments

### Host

Specifies the host or IP address of the service to test.

Example:

```text
127.0.0.1
```

### Port

Specifies the target service port.

Examples:

```text
5173
3000
3001
```

### --path

Specifies the HTTP path to test.

Example:

```text
--path /
```

### --method

Specifies the HTTP method.

Supported methods:

```text
GET
POST
```

Example:

```text
--method GET
```

### --data

Specifies JSON data for POST requests.

Example:

```text
--data "{\"username\":\"USERNAME\",\"password\":\"PASSWORD\"}"
```

### --token

Specifies a JWT to be sent using the HTTP Authorization header.

The header is sent as:

```text
Authorization: Bearer <JWT>
```

Example:

```text
--token "<JWT>"
```

### -n / --requests

Specifies the total number of requests.

Example:

```text
-n 1000
```

### -c / --concurrency

Specifies the maximum number of simultaneous requests.

Example:

```text
-c 50
```

### --timeout

Specifies the maximum timeout for each request.

Example:

```text
--timeout 5
```

---

## GET Request Example

The following command performs 100 requests against the Frontend with 10 concurrent requests:

```text
py -3 ddos.py 127.0.0.1 5173 --path / -n 100 -c 10
```

---

## POST Request Example

The LDAP HTTP service uses the `/login` endpoint to authenticate users and generate a JWT.

Example:

```text
py -3 ddos.py 127.0.0.1 3001 --path /login --method POST --data "{\"username\":\"USERNAME\",\"password\":\"PASSWORD\"}" -n 100 -c 10
```

Valid laboratory credentials were used during testing.

The generated JWT was not stored in this repository.

---

## JWT Authentication

The Backend protects the `/products` endpoint using JWT authentication.

The authentication process was:

```text
LDAP /login
     |
     | JWT
     v
Load Testing Script
     |
     | Authorization: Bearer <JWT>
     v
Backend /products
```

A JWT was obtained from the LDAP service and then passed to the load testing script using the `--token` parameter.

The token was generated dynamically during testing and was not stored in the source code or repository.

The `/products` endpoint was successfully tested using the generated JWT.

---

## Fail2Ban Protection

The three Docker services were protected using Fail2Ban.

The active Fail2Ban jails were:

```text
elf-nginx
elf-backend
elf-ldap-http
elf-ldap-tls
```

The corresponding log files were configured for monitoring:

```text
Frontend:
C:\Users\Melfl\elf-dashboard\logs\http.log

Backend:
C:\Users\Melfl\elf-backend\logs\http.log

LDAP HTTP:
C:\Users\Melfl\elf-ldap\logs\http.log

LDAP TLS:
C:\Users\Melfl\elf-ldap\logs\tls.log
```

The LDAP TLS service has an additional Fail2Ban protection at the port level.

The TLS protection was configured for:

```text
Port: 636
```

The configuration was verified as:

```text
[elf-ldap-tls]
port = 636
```

---

## JWT Console Log Removal

The Frontend was reviewed and the console logging associated with the JWT was removed.

The Frontend was rebuilt after the modification to verify that the application remained compilable.

The production build completed successfully after the change.

---

# Load Testing Methodology

The load tests were performed progressively.

The total number of requests and the number of concurrent requests were increased between tests.

For every test, the following values were recorded:

- Completed requests
- HTTP 2xx responses
- HTTP 4xx/5xx responses
- Connection errors
- Total execution time
- Average response time
- Requests per second

A configuration was considered stable when:

```text
100% HTTP 2xx responses
0 HTTP 4xx/5xx responses
0 connection errors
```

When a higher configuration produced connection errors, the previous configuration with no errors was considered the highest stable configuration tested.

The purpose was to determine the highest tested load that each service could handle without connection errors.

---

# Frontend Load Test

Target:

```text
http://127.0.0.1:5173/
```

The Frontend was tested using progressively higher request and concurrency values.

| Requests | Concurrency | HTTP 2xx | HTTP 4xx/5xx | Connection Errors | Requests/Second |
|---:|---:|---:|---:|---:|---:|
| 6,000 | 240 | 6,000 | 0 | 0 | 811.25 |
| 6,500 | 260 | 6,500 | 0 | 0 | 1,048.05 |
| 6,625 | 265 | 6,625 | 0 | 0 | 951.62 |
| 6,687 | 267 | 3,911 | 0 | 2,776 | 945.78 |
| 6,750 | 270 | 5,694 | 0 | 1,056 | 884.62 |
| 7,000 | 280 | 4,012 | 0 | 2,988 | 964.83 |

## Frontend Maximum Stable Tested Load

The highest stable configuration tested was:

```text
6,625 requests
265 concurrent requests
```

Result:

```text
Completed requests     : 6625
HTTP 2xx               : 6625
HTTP 4xx/5xx           : 0
Connection errors      : 0
Total time             : 6.96 s
Average response time  : 0.2654 s
Requests per second    : 951.62
```

The next tested configuration produced connection errors:

```text
6,687 requests
267 concurrent requests
2,776 connection errors
```

Therefore, the highest stable tested configuration for the Frontend was:

**6,625 requests with 265 concurrent requests.**

---

# Backend Load Test

Target:

```text
http://127.0.0.1:3000/products
```

The `/products` endpoint requires JWT authentication.

The Backend was tested using progressively higher request and concurrency values.

| Requests | Concurrency | HTTP 2xx | HTTP 4xx/5xx | Connection Errors | Requests/Second |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 0 | 0 | 15.95 |
| 100 | 10 | 100 | 0 | 0 | 271.09 |
| 500 | 25 | 500 | 0 | 0 | 372.81 |
| 1,000 | 50 | 1,000 | 0 | 0 | 351.33 |
| 2,000 | 100 | 2,000 | 0 | 0 | 437.12 |
| 5,000 | 200 | 5,000 | 0 | 0 | 356.33 |
| 7,500 | 300 | 7,500 | 0 | 0 | 399.30 |
| 10,000 | 500 | 10,000 | 0 | 0 | 350.77 |
| 10,500 | 525 | 10,499 | 0 | 1 | 365.08 |
| 11,000 | 550 | 10,975 | 0 | 25 | 376.77 |
| 12,500 | 625 | 12,332 | 0 | 168 | 354.81 |

## Backend Maximum Stable Tested Load

The highest stable configuration tested was:

```text
10,000 requests
500 concurrent requests
```

Result:

```text
Completed requests     : 10000
HTTP 2xx               : 10000
HTTP 4xx/5xx           : 0
Connection errors      : 0
Total time             : 28.51 s
Average response time  : 1.3746 s
Requests per second    : 350.77
```

The next tested configuration produced a connection error:

```text
10,500 requests
525 concurrent requests
1 connection error
```

Therefore, the highest stable tested configuration for the Backend was:

**10,000 requests with 500 concurrent requests.**

---

# LDAP HTTP Load Test

Target:

```text
http://127.0.0.1:3001/login
```

The `/login` endpoint was tested using valid laboratory credentials to evaluate authentication and JWT generation under load.

| Requests | Concurrency | HTTP 2xx | HTTP 4xx/5xx | Connection Errors | Requests/Second |
|---:|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 0 | 0 | 23.84 |
| 100 | 10 | 100 | 0 | 0 | 260.57 |
| 500 | 25 | 500 | 0 | 0 | 287.69 |
| 1,000 | 50 | 1,000 | 0 | 0 | 389.11 |
| 2,000 | 100 | 2,000 | 0 | 0 | 507.51 |
| 5,000 | 200 | 5,000 | 0 | 0 | 448.88 |
| 7,500 | 300 | 7,500 | 0 | 0 | 281.40 |
| 10,000 | 500 | 10,000 | 0 | 0 | 348.53 |
| 10,500 | 525 | 10,500 | 0 | 0 | 386.02 |
| 11,000 | 550 | 10,986 | 0 | 14 | 382.47 |
| 12,500 | 625 | 12,090 | 0 | 410 | 296.82 |

## LDAP Maximum Stable Tested Load

The highest stable configuration tested was:

```text
10,500 requests
525 concurrent requests
```

Result:

```text
Completed requests     : 10500
HTTP 2xx               : 10500
HTTP 4xx/5xx           : 0
Connection errors      : 0
Total time             : 27.20 s
Average response time  : 1.3113 s
Requests per second    : 386.02
```

The next tested configuration produced connection errors:

```text
11,000 requests
550 concurrent requests
14 connection errors
```

Therefore, the highest stable tested configuration for LDAP HTTP was:

**10,500 requests with 525 concurrent requests.**

---

# Load Test Summary

| Service | Port | Maximum Stable Tested Requests | Concurrency |
|---|---:|---:|---:|
| Frontend | 5173 | 6,625 | 265 |
| Backend | 3000 | 10,000 | 500 |
| LDAP HTTP | 3001 | 10,500 | 525 |

These values represent the highest stable configurations tested in the local laboratory environment.

---

# How the Maximum Stable Load Was Determined

The load test followed a progressive approach.

First, a low number of requests was executed to verify that the script and service were working correctly.

The load was then increased by modifying:

```text
-n
-c
```

where:

- `-n` represents the total number of requests.
- `-c` represents the maximum number of concurrent requests.

After each test, the HTTP status codes and connection errors were reviewed.

The highest configuration with 100% successful HTTP 2xx responses and zero connection errors was recorded as the maximum stable tested load.

When the next higher configuration produced connection errors, the previous successful configuration was selected as the final stable value.

The final values were:

```text
Frontend: 6,625 requests / 265 concurrent requests

Backend: 10,000 requests / 500 concurrent requests

LDAP HTTP: 10,500 requests / 525 concurrent requests
```

---

# Post-Test Validation

After the load tests, the services were tested again to verify that they remained operational.

The Frontend returned:

```text
HTTP/1.1 200 OK
```

The Backend returned:

```text
HTTP/1.1 200 OK
```

with the response:

```json
{
  "message": "e.l.f. Backend running"
}
```

These checks confirmed that the services remained available after the controlled load tests.

---

# Security Summary

The security-related changes implemented during the practice were:

- Fail2Ban protection for the Frontend HTTP service.
- Fail2Ban protection for the Backend HTTP service.
- Fail2Ban protection for the LDAP HTTP service.
- Additional Fail2Ban protection for LDAP TLS on port 636.
- HTTP request logging for the protected services.
- JWT authentication for the Backend `/products` endpoint.
- Removal of the JWT-related `console.log` from the Frontend.
- The load testing script was kept outside the Docker images.

---

# Limitations

The tests were performed in a local Docker laboratory environment.

The results depend on:

- Available computer resources
- Docker configuration
- Nginx configuration
- Node.js configuration
- Operating system
- Network configuration
- Number of concurrent requests
- Service response time

Therefore, these results represent laboratory measurements and should not be interpreted as guaranteed production capacity.

---

# Conclusion

The controlled load tests allowed the Frontend, Backend, and LDAP HTTP services to be evaluated under progressively higher levels of HTTP traffic.

The highest stable configurations tested were:

```text
Frontend:
6,625 requests / 265 concurrent requests

Backend:
10,000 requests / 500 concurrent requests

LDAP HTTP:
10,500 requests / 525 concurrent requests
```

Higher configurations produced connection errors, allowing the highest stable tested configuration to be identified for each service.

The `ddos.py` script was modified to accept the target host and port as command-line arguments and to support HTTP methods, JSON request data, JWT authentication, request count, concurrency, and timeout configuration.

The script was executed outside the three Docker images as required by the practice.

Fail2Ban protection was implemented for the Frontend, Backend, LDAP HTTP, and LDAP TLS services, with additional port-level protection configured for LDAP TLS on port 636.

The JWT console logging was removed from the Frontend and the application was rebuilt successfully after the modification.