# CS 460 Networking Reference

This is a consolidated reference for the packet structures implemented in CS 460. The diagrams describe the bytes handled by the labs, not every field that appears on a physical network.

# Table of Contents

 - [Overview](#0-overview)
 - [Ethernet](#1-ethernet)
 - [ARP packet](#2-arp-packet)
 - [IPv4 header](#3-ipv4-header)
 - [UDP header](#4-udp-header)
 - [TCP header](#5-tcp-header)
 - [ICMP header](#6-icmp-header)
 - [Various Notes](#7-various-notes)
	 - [Endianness](#endianness)
	 - [Layering Options](#layering-options)

## Overview

Each packet structure is shown separately below. The columns are bit positions within a 32-bit row; fields are labeled above the space they occupy. The Ethernet frame is simplified to simply show eight bits per column, with the row being all the bits in an Ethernet frame, rather than just 32 bits.

A table giving the **Field**, **Size**, and **Description** of each field follows. There is another column called **Example** giving example bytes for each field. Asterisks are for fields where bytes are shared between fields. In these cases, a short paragraph titled **Shared Bytes** follows the table for an explanation.

Finally, at the bottom is all the bytes from the example concatenated together, giving a complete example of a given packet structure.

## Ethernet

### Ethernet frame

<table border="1" style="border:3px solid black;">
<tr><th>00</th><th>08</th><th>16</th><th>24</th><th>32</th><th>40</th><th>48</th><th>56</th><th>64</th><th>72</th><th>80</th><th>88</th><th>96</th><th>104</th></tr>
<tr><td colspan="6">Destination MAC</td><td colspan="6">Source MAC</td><td colspan="2">EtherType</td></tr>
</table>

### 802.1Q VLAN Ethernet frame

<table border="1" style="border:3px solid black;">
<tr><th>00</th><th>08</th><th>16</th><th>24</th><th>32</th><th>40</th><th>48</th><th>56</th><th>64</th><th>72</th><th>80</th><th>88</th><th>96</th><th>104</th><th>112</th><th>120</th><th>128</th><th>136</th></tr>
<tr><td colspan="6">Destination MAC</td><td colspan="6">Source MAC</td><td colspan="4">802.1Q Header</td><td colspan="2">EtherType</td></tr>
</table>

| Field | Size | Description | Example |
| --- | ---: | --- | --- |
| Destination MAC address | 6 bytes | Intended receiver; `ff:ff:ff:ff:ff:ff` is broadcast | <code style="color:#d9534f">01 02 03 04 05 06</code> |
| Source MAC address | 6 bytes | Sender on the local link | <code style="color:#5cb85c">aa bb cc dd ee ff</code> |
| 802.1Q header | 4 bytes | An optional tag to support VLANs | <code style="color:#5bc0de">81 00 00 19</code> |
| EtherType | 2 bytes | Identifies the payload protocol | <code style="color:#f0ad4e">08 00</code> |
| *Payload* | *variable* | Usually an IPv4 datagram or ARP packet. | N/A |

#### Full Example:
<pre><code><span style="color:#d9534f">01 02 03 04 05 06</span> <span style="color:#5cb85c">aa bb cc dd ee ff</span> <span style="color:#5bc0de">81 00 00 19</span> <span style="color:#f0ad4e">08 00</span></code></pre>

## ARP packet

<table border="1" style="border:3px solid black;">
<tr>
<th>00</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th>
<th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th>
<th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th>
<th>24</th><th>25</th><th>26</th><th>27</th><th>28</th><th>29</th><th>30</th><th>31</th></tr>
<tr><td colspan="16">Hardware type</td><td colspan="16">Protocol type</td></tr>
<tr><td colspan="8">Hardware address length</td><td colspan="8">Protocol address length</td><td colspan="16">Opcode</td></tr>
<tr><td colspan="32">Sender hardware address (bytes 0-3)</td></tr>
<tr><td colspan="16">Sender hardware address (bytes 4-5)</td><td colspan="16">Sender protocol address (bytes 0-1)</td></tr>
<tr><td colspan="16">Sender protocol address (bytes 2-3)</td><td colspan="16">Target hardware address (bytes 0-1)</td></tr>
<tr><td colspan="32">Target hardware address (bytes 2-5)</td></tr>
<tr><td colspan="32">Target protocol address</td></tr>
<tr><td colspan="32">Data</td></tr>
</table>

| Field | Size | Description | Example |
| --- | ---: | --- | --- |
| Hardware type | 2 bytes | Ethernet: `ARPHRD_ETHER = 1` | <code style="color:#d9534f">00 01</code> |
| Protocol type | 2 bytes | IPv4: `ETH_P_IP = 0x0800` | <code style="color:#5cb85c">08 00</code> |
| Hardware address length | 1 byte | Ethernet MAC length: `6` | <code style="color:#5bc0de">06</code> |
| Protocol address length | 1 byte | IPv4 address length: `4` | <code style="color:#f0ad4e">04</code> |
| Opcode | 2 bytes | Request `1`, reply `2` | <code style="color:#d9534f">00 01</code> |
| Sender hardware address | 6 bytes | Sender MAC | <code style="color:#5cb85c">11 22 33 44 55 66</code> |
| Sender protocol address | 4 bytes | Sender IPv4 address | <code style="color:#5bc0de">c0 00 02 01</code> |
| Target hardware address | 6 bytes | Target MAC; may be zero in a request | <code style="color:#f0ad4e">aa bb cc dd ee ff</code> |
| Target protocol address | 4 bytes | Target IPv4 address | <code style="color:#d9534f">c0 00 02 02</code> |
| *Data* | *variable* | Not needed for the basic lab | N/A |

#### Full Example:
<pre><code><span style="color:#d9534f">00 01</span> <span style="color:#5cb85c">08 00</span> <span style="color:#5bc0de">06</span> <span style="color:#f0ad4e">04</span> <span style="color:#d9534f">00 01</span> <span style="color:#5cb85c">11 22 33 44 55 66</span> <span style="color:#5bc0de">c0 00 02 01</span> <span style="color:#f0ad4e">aa bb cc dd ee ff</span> <span style="color:#d9534f">c0 00 02 02</span></code></pre>

## IPv4 header

<table border="1" style="border:3px solid black;">
<tr><th>00</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th><th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th><th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th><th>24</th><th>25</th><th>26</th><th>27</th><th>28</th><th>29</th><th>30</th><th>31</th></tr>
<tr><td colspan="4">Version</td><td colspan="4">IHL</td><td colspan="6">DSCP</td><td colspan="2">ECN</td><td colspan="16">Total length</td></tr>
<tr><td colspan="16">Identification</td><td colspan="3">Flags</td><td colspan="13">Fragment offset</td></tr>
<tr><td colspan="8">TTL</td><td colspan="8">Protocol</td><td colspan="16">Header checksum</td></tr>
<tr><td colspan="32">Source address</td></tr>
<tr><td colspan="32">Destination address</td></tr>
</table>

| Field | Size | Notes | Example |
| --- | ---: | --- | --- |
| Version | 4 bits | IPv4 value is `4` | <code style="color:#d9534f">45</code> * |
| IHL | 4 bits | Header length in 32-bit words; `5` means 20 bytes | * |
| DSCP | 6 bits | In this class, set to `0` | <code style="color:#5cb85c">00</code> * |
| ECN | 2 bits | In this class, set to `0` | * |
| Total length | 2 bytes | IPv4 header plus payload | <code style="color:#5bc0de">00 21</code> |
| Identification | 2 bytes | Fragmentation support | <code style="color:#f0ad4e">12 34</code> |
| Flags | 3 bits | Fragmentation control | <code style="color:#d9534f">40 00</code> * |
| Fragment offset | 13 bits | Fragmentation support | * |
| TTL | 1 byte | Decremented by each router | <code style="color:#5cb85c">40</code> |
| Protocol | 1 byte | Identifies the next payload protocol | <code style="color:#5bc0de">11</code> |
| Header checksum | 2 bytes | Covers the IPv4 header | <code style="color:#f0ad4e">00 00</code> |
| Source address | 4 bytes | Sender IPv4 address | <code style="color:#d9534f">c0 00 02 01</code> |
| Destination address | 4 bytes | Receiver IPv4 address | <code style="color:#5cb85c">c0 00 02 02</code> |
| Options and padding | *variable* | Included only when IHL is greater than 5 | N/A |
| *Payload* | *variable* | UDP, TCP, ICMP, or another protocol | N/A |

**Shared Bytes:** Asterisks are for bytes that are shared between fields. Byte <code style="color:#d9534f">45</code> is ``01000101``: the first four bits, ``0100``, contains Version ``4``, and the last four bits, ``0101``, contains IHL ``5``. Byte <code style="color:#5cb85c">00</code> is ``00000000``: the first six bits are ``0`` for DSCP, and last two bits are ``0`` for ECN. Bytes <code style="color:#d9534f">40 00</code> are ``01000000 00000000``: the first 3 bits, ``010``, are the Flags (Reserved ``0``, Don't Fragment/DF ``1``, More Fragments/MF ``0``), and the remaining 13 bits are the Fragment Offset, ``0``.

#### Full Example:
<pre><code><span style="color:#d9534f">45</span> <span style="color:#5cb85c">00</span> <span style="color:#5bc0de">00 21</span> <span style="color:#f0ad4e">12 34</span> <span style="color:#d9534f">40 00</span> <span style="color:#5cb85c">40</span> <span style="color:#5bc0de">11</span> <span style="color:#f0ad4e">00 00</span> <span style="color:#d9534f">c0 00 02 01</span> <span style="color:#5cb85c">c0 00 02 02</span></code></pre>

## UDP header

<table border="1" style="border:3px solid black;">
<tr><th>00</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th><th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th><th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th><th>24</th><th>25</th><th>26</th><th>27</th><th>28</th><th>29</th><th>30</th><th>31</th></tr>
<tr><td colspan="16">Source port</td><td colspan="16">Destination port</td></tr>
<tr><td colspan="16">Length</td><td colspan="16">Checksum</td></tr>
</table>

| Field | Size | Description | Example |
| --- | ---: | --- | --- |
| Source port | 2 bytes | Sending application port | <code style="color:#d9534f">0f a0</code> |
| Destination port | 2 bytes | Receiving application port | <code style="color:#5cb85c">04 d2</code> |
| Length | 2 bytes | UDP header plus UDP payload | <code style="color:#5bc0de">00 0d</code> |
| Checksum | 2 bytes | Set to zero in the transport lab | <code style="color:#f0ad4e">00 00</code> |
| *Data* | *variable* | Application payload | <code style="color:#d9534f">68 65 6c 6c 6f</code> |

#### Full Example:
<pre><code><span style="color:#d9534f">0f a0</span> <span style="color:#5cb85c">04 d2</span> <span style="color:#5bc0de">00 0d</span> <span style="color:#f0ad4e">00 00</span> <span style="color:#d9534f">68 65 6c 6c 6f</span></code></pre>

## TCP header

<table border="1">
<tr><th>00</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th><th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th><th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th><th>24</th><th>25</th><th>26</th><th>27</th><th>28</th><th>29</th><th>30</th><th>31</th></tr>
<tr><td colspan="16">Source port</td><td colspan="16">Destination port</td></tr>
<tr><td colspan="32">Sequence number</td></tr>
<tr><td colspan="32">Acknowledgment number</td></tr>
<tr><td colspan="4">Data offset</td><td colspan="3">Reserved</td><td colspan="3">ECN</td><td colspan="6">Control bits</td><td colspan="16">Window</td></tr>
<tr><td colspan="16">Checksum</td><td colspan="16">Urgent pointer</td></tr>
<tr><td colspan="32">Options and padding</td></tr>
</table>

| Field | Size | Description | Example |
| --- | ---: | --- | --- |
| Source port | 2 bytes | Sending application port | <code style="color:#d9534f">0f a0</code> |
| Destination port | 2 bytes | Receiving application port | <code style="color:#5cb85c">04 d2</code> |
| Sequence number | 4 bytes | Position of segment data in the byte stream | <code style="color:#5bc0de">11 22 33 44</code> |
| Acknowledgment number | 4 bytes | Next byte expected by the sender of the ACK | <code style="color:#f0ad4e">11 22 33 44</code> |
| Data offset | 4 bits | Header length in 4-byte words; `5` means 20 bytes | <code style="color:#d9534f">50 12</code> * |
| Reserved | 3 bits | `000` in the lab; not currently used | * |
| ECN | 3 bits | `000` in the lab | * |
| Control bits | 6 bits | `URG`, `ACK`, `PSH`, `RST`, `SYN`, `FIN` | * |
| Window | 2 bytes | Advertised receive window; 64 is used as a reasonable lab value | <code style="color:#5cb85c">00 40</code> |
| Checksum | 2 bytes | Set to zero in the transport lab | <code style="color:#5bc0de">00 00</code> |
| Urgent pointer | 2 bytes | Not used in the lab | <code style="color:#f0ad4e">00 00</code> |
| Options and padding | *variable* | Makes the header a multiple of 4 bytes | N/A |
| *Data* | *variable* | Application payload | <code style="color:#d9534f">68 65 6c 6c 6f</code> |

**Shared Bytes:** Asterisks are for bytes that are shared between fields. Bytes <code style="color:#d9534f">50 12</code> are ``01010000 00010010``: The first four bits ``0101`` are the Data Offset, equaling ``5`` words (20 bytes). The next three bits ``000`` are Reserved, which is just set to ``0``. The next three bits ``000`` are for ECN, and the last six bits, ``010010``, are the Control Bits, equaling ACK + SYN (using the order URG, ACK, PSH, RST, SYN, FIN). The packed fields concatenate as ``0101 000 000 010010``.

#### Full Example:
<pre><code><span style="color:#d9534f">0f a0</span> <span style="color:#5cb85c">04 d2</span> <span style="color:#5bc0de">11 22 33 44</span> <span style="color:#f0ad4e">11 22 33 44</span> <span style="color:#d9534f">50 12</span> <span style="color:#5cb85c">00 40</span> <span style="color:#5bc0de">00 00</span> <span style="color:#f0ad4e">00 00</span> <span style="color:#d9534f">68 65 6c 6c 6f</span></code></pre>

## ICMP header

<table border="1">
<tr><th>00</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th><th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th><th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th><th>24</th><th>25</th><th>26</th><th>27</th><th>28</th><th>29</th><th>30</th><th>31</th></tr>
<tr><td colspan="8">Type</td><td colspan="8">Code</td><td colspan="16">Checksum</td></tr>
<tr><td colspan="32">Message-specific fields and data</td></tr>
</table>

| Field | Size | Description | Example |
| --- | ---: | --- | --- |
| Type | 1 byte | Identifies the ICMP message type | <code style="color:#d9534f">08</code> |
| Code | 1 byte | Provides additional context for the message type | <code style="color:#5cb85c">00</code> |
| Checksum | 2 bytes | Covers the ICMP header and message data | <code style="color:#5bc0de">00 00</code> |
| Message-specific fields and data | *variable* | Depends on the ICMP message type | <code style="color:#f0ad4e">00 01 00 01 68 65 6c 6c 6f</code> |

#### Full Example:
<pre><code><span style="color:#d9534f">08</span> <span style="color:#5cb85c">00</span> <span style="color:#5bc0de">00 00</span> <span style="color:#f0ad4e">00 01 00 01 68 65 6c 6c 6f</span></code></pre>

## Various Notes

### Endianness

In this class, **network byte order** will be used, which is **big-endian**. You likely will not have to worry about this at all in this class, but this needs to be noted.

Examples below use the same numeric value in both byte orders. The bit order within each byte does not change; only the order of complete bytes changes.

| Value size | Numeric value | Big-endian bytes | Little-endian bytes |
| --- | --- | --- | --- |
| 1 byte | `0x12` | `12` | `12` |
| 2 bytes | `0x1234` | `12 34` | `34 12` |
| 4 bytes | `0x12345678` | `12 34 56 78` | `78 56 34 12` |

For example, the 16-bit value `0x1234` is transmitted as `12 34` in network byte order. Optional further reading: [Endianness - Wikipedia](https://en.wikipedia.org/wiki/Endianness).

### Layering Options

These are the main protocol combinations used in the labs:

```text
Ethernet Frame -> IPv4 -> UDP
Ethernet Frame -> IPv4 -> TCP
Ethernet Frame -> IPv4 -> ICMP
Ethernet Frame -> ARP
```

Note that you may not construct these full combinations. For instance, in the first lab, link-layer, you will only construct the Ethernet Frame - no payload inside it. However, it is important to remember how the OSI model behind this uses abstraction layers.