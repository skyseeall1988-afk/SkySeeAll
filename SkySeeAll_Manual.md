
# SkySeeAll Getting Started Guide

## 1. Overview

Welcome to the SkySeeAll application. This guide will help you get started with the core tools and features of this B2G security and network analysis platform.

SkySeeAll is designed to provide a comprehensive suite of tools for network discovery, security assessment, and data analysis, all accessible from a convenient web-based dashboard.

**Core Components:**

*   **SkySeeAll Dashboard:** A web-based terminal for interacting with the system and its tools.
*   **`nmap`:** A powerful network scanner for discovering hosts, services, and vulnerabilities.
*   **`bettercap`:** A versatile framework for network analysis and man-in-the-middle attacks.
*   **`aircrack-ng`:** A suite of tools for Wi-Fi network security assessment.

---

## 2. The Dashboard

The SkySeeAll dashboard provides a web-based terminal, giving you full command-line access to the system.

**Starting the Dashboard:**

The dashboard should already be running. You can access it at:
[http://localhost:3000](http://localhost:3000)

---

## 3. Core Tools

The following tools are pre-installed and ready to be used from the dashboard terminal.

### 3.1. `nmap` (Network Mapper)

`nmap` is an essential tool for network discovery and security auditing.

**Example Usage:**

*   **Ping Scan (Discover Hosts):**
    This scan will find all active devices on a given network range.
    ```bash
    /data/data/com.termux/files/usr/bin/nmap -sn <network_range>
    # Example: /data/data/com.termux/files/usr/bin/nmap -sn 192.168.1.0/24
    ```

*   **Detailed Scan (Services and OS Detection):**
    This scan will probe a specific host to identify open ports, the services running on them, and the operating system.
    ```bash
    /data/data/com.termux/files/usr/bin/nmap -sV -O <target_ip>
    # Example: /data/data/com.termux/files/usr/bin/nmap -sV -O 192.168.1.101
    ```

### 3.2. `bettercap`

`bettercap` is a powerful framework for network analysis and man-in-the-middle (MITM) attacks.

**Example Usage:**

1.  **Start `bettercap` in interactive mode:**
    ```bash
    /data/data/com.termux/files/home/usr/local/bin/bettercap
    ```

2.  **Discover hosts on the network:**
    (Inside the `bettercap` prompt)
    ```
    net.probe on
    ```

3.  **Show discovered hosts:**
    (Inside the `bettercap` prompt)
    ```
    net.show
    ```

4.  **Start sniffing for credentials and data:**
    (Inside the `bettercap` prompt)
    ```
    sniffer on
    ```

5.  **Show sniffed data:**
    (Inside the `bettercap` prompt)
    ```
    sniffer show
    ```

### 3.3. `aircrack-ng`

`aircrack-ng` is a suite of tools for Wi-Fi network security. It can be used for monitoring, attacking, and cracking Wi-Fi networks.

**Example Usage (WEP Cracking):**

This example assumes you have a capture file (`.cap`) containing WEP encrypted packets.

```bash
/data/data/com.termux/files/home/usr/local/bin/aircrack-ng /path/to/your/capture.cap
```

---

## 4. Advanced Techniques

### 4.1. Reverse Shells

A reverse shell is a technique used to gain remote access to a machine. We have demonstrated how to set up a reverse shell using `netcat`. This is a powerful technique for post-exploitation.

---

## 5. Disclaimer

The tools included in the SkySeeAll application are powerful and should be used responsibly and in accordance with all applicable laws and regulations. Ensure you have proper authorization before using these tools on any network or system.
