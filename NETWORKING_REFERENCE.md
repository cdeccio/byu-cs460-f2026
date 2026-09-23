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

## 0. Overview

Each packet structure is shown separately below. The columns are bit positions within a 32-bit row; fields are labeled above the space they occupy. The Ethernet frame is simplified to simply show eight bits per column, with the row being all the bits in an Ethernet frame, rather than just 32 bits.

A table giving the **Field**, **Size**, and **Description** of each field follows. There is another column called **Example** giving example bytes for each field. Asterisks are for fields where bytes are shared between fields. In these cases, a short paragraph titled **Shared Bytes** follows the table for an explanation.

Finally, at the bottom is all the bytes from the example concatenated together, giving a complete example of a given packet structure.

## 1. Ethernet

### Ethernet frame

<table border="1">
<tr><th>00</th><th>08</th><th>16</th><th>24</th><th>32</th><th>40</th><th>48</th><th>56</th><th>64</th><th>72</th><th>80</th><th>88</th><th>96</th><th>104</th></tr>
<tr><td colspan="6">Destination MAC</td><td colspan="6">Source MAC</td><td colspan="2">EtherType</td></tr>
</table>

### 802.1Q VLAN Ethernet frame

<table border="1">
<tr><th>00</th><th>08</th><th>16</th><th>24</th><th>32</th><th>40</th><th>48</th><th>56</th><th>64</th><th>72</th><th>80</th><th>88</th><th>96</th><th>104</th><th>112</th><th>120</th><th>128</th><th>136</th></tr>
<tr><td colspan="6">Destination MAC</td><td colspan="6">Source MAC</td><td colspan="4">802.1Q Header</td><td colspan="2">EtherType</td></tr>
</table>

| Field | Size | Description | Example |
| --- | ---: | --- | --- |
| Destination MAC address | 6 bytes | Intended receiver; `ff:ff:ff:ff:ff:ff` is broadcast | `02 00 00 00 00 02` |
| Source MAC address | 6 bytes | Sender on the local link | `02 00 00 00 00 01` |
| 802.1Q header | 4 bytes | An optional tag to support VLANs | `81 00 00 19` |
| EtherType | 2 bytes | Identifies the payload protocol | `08 00` |
| *Payload* | *variable* | Usually an IPv4 datagram or ARP packet. | N/A |

```text
02 00 00 00 00 02 02 00 00 00 00 01 81 00 00 19 08 00
```

## 2. ARP packet

<table border="1">
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
| Hardware type | 2 bytes | Ethernet: `ARPHRD_ETHER = 1` | `00 01` |
| Protocol type | 2 bytes | IPv4: `ETH_P_IP = 0x0800` | `08 00` |
| Hardware address length | 1 byte | Ethernet MAC length: `6` | `06` |
| Protocol address length | 1 byte | IPv4 address length: `4` | `04` |
| Opcode | 2 bytes | Request `1`, reply `2` | `00 01` |
| Sender hardware address | 6 bytes | Sender MAC | `02 00 00 00 00 01` |
| Sender protocol address | 4 bytes | Sender IPv4 address | `c0 00 02 01` |
| Target hardware address | 6 bytes | Target MAC; may be zero in a request | `00 00 00 00 00 00` |
| Target protocol address | 4 bytes | Target IPv4 address | `c0 00 02 02` |
| *Data* | *variable* | Not needed for the basic lab | N/A |

```text
00 01 08 00 06 04 00 01 02 00 00 00 00 01 c0 00
02 01 00 00 00 00 00 00 00 00 00 00 c0 00 02 02
```

## 3. IPv4 header

<table border="1">
<tr><th>00</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th><th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th><th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th><th>24</th><th>25</th><th>26</th><th>27</th><th>28</th><th>29</th><th>30</th><th>31</th></tr>
<tr><td colspan="4">Version</td><td colspan="4">IHL</td><td colspan="6">DSCP</td><td colspan="2">ECN</td><td colspan="16">Total length</td></tr>
<tr><td colspan="16">Identification</td><td colspan="3">Flags</td><td colspan="13">Fragment offset</td></tr>
<tr><td colspan="8">TTL</td><td colspan="8">Protocol</td><td colspan="16">Header checksum</td></tr>
<tr><td colspan="32">Source address</td></tr>
<tr><td colspan="32">Destination address</td></tr>
</table>

| Field | Size | Notes | Example |
| --- | ---: | --- | --- |
| Version | 4 bits | IPv4 value is `4` | `45` * |
| IHL | 4 bits | Header length in 32-bit words; `5` means 20 bytes | `45` * |
| DSCP | 6 bits | In this class, set to `0` | `00` * |
| ECN | 2 bits | In this class, set to `0` | `00` * |
| Total length | 2 bytes | IPv4 header plus payload | `00 21` |
| Identification | 2 bytes | Fragmentation support | `12 34` |
| Flags | 3 bits | Fragmentation control | `40 00` * |
| Fragment offset | 13 bits | Fragmentation support | `40 00` * |
| TTL | 1 byte | Decremented by each router | `40` |
| Protocol | 1 byte | Identifies the next payload protocol | `11` |
| Header checksum | 2 bytes | Covers the IPv4 header | `00 00` |
| Source address | 4 bytes | Sender IPv4 address | `c0 00 02 01` |
| Destination address | 4 bytes | Receiver IPv4 address | `c0 00 02 02` |
| Options and padding | variable | Included only when IHL is greater than 5 | N/A |
| *Payload* | *variable* | UDP, TCP, ICMP, or another protocol | N/A |

**Shared Bytes:** IPv4 byte ``45`` contains Version ``4`` and IHL ``5``. Byte ``00`` for DSCP/ECN is just `0` for DSCP and ``0`` for ECN. Bytes ``40 00`` are ``0100000000000000``: the first 3 bits, ``010``, are the Flags (Reserved ``0``, Don't Fragment/DF ``1``, More Fragments/MF ``0``), and the remaining 13 bits are the Fragment Offset, ``0``.

```text
45 00 00 21 12 34 40 00 40 11 00 00 c0 00 02 01
c0 00 02 02
```

## 4. UDP header

<table border="1">
<tr><th>00</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th><th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th><th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th><th>24</th><th>25</th><th>26</th><th>27</th><th>28</th><th>29</th><th>30</th><th>31</th></tr>
<tr><td colspan="16">Source port</td><td colspan="16">Destination port</td></tr>
<tr><td colspan="16">Length</td><td colspan="16">Checksum</td></tr>
</table>

| Field | Size | Description | Example |
| --- | ---: | --- | --- |
| Source port | 2 bytes | Sending application port | `0f a0` |
| Destination port | 2 bytes | Receiving application port | `04 d2` |
| Length | 2 bytes | UDP header plus UDP payload | `00 0d` |
| Checksum | 2 bytes | Set to zero in the transport lab | `00 00` |
| *Data* | *variable* | Application payload | `68 65 6c 6c 6f` |

```text
0f a0 04 d2 00 0d 00 00 68 65 6c 6c 6f
```

## 5. TCP header

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
| Source port | 2 bytes | Sending application port | `0f a0` |
| Destination port | 2 bytes | Receiving application port | `04 d2` |
| Sequence number | 4 bytes | Position of segment data in the byte stream | `00 00 00 01` |
| Acknowledgment number | 4 bytes | Next byte expected by the sender of the ACK | `00 00 00 01` |
| Data offset | 4 bits | Header length in 4-byte words; `5` means 20 bytes | `50 92` * |
| Reserved | 3 bits | `000` in the lab; not currently used | `50 92` * |
| ECN | 3 bits | Not used in the lab | `50 92` * |
| Control bits | 6 bits | `URG`, `ACK`, `PSH`, `RST`, `SYN`, `FIN` | `50 92` * |
| Window | 2 bytes | Advertised receive window; 64 is used as a reasonable lab value | `00 40` |
| Checksum | 2 bytes | Set to zero in the transport lab | `00 00` |
| Urgent pointer | 2 bytes | Not used in the lab | `00 00` |
| Options and padding | *variable* | Makes the header a multiple of 4 bytes | N/A |
| *Data* | *variable* | Application payload | `68 65 6c 6c 6f` |

**Shared Bytes:** TCP bytes ``50 92`` contain the packed fields: Data Offset ``0101`` = 5 words (20 bytes), Reserved ``000`` = 0, ECN ``010``, and Control Bits ``010010`` = ACK + SYN (using the order URG, ACK, PSH, RST, SYN, FIN). The packed fields concatenate as ``0101 000 010 010010`` or ``0101000010010010``.

```text
0f a0 04 d2 00 00 00 01 00 00 00 01 50 92 00 40
00 00 00 00 00 00 68 65 6c 6c 6f
```

## 6. ICMP header

<table border="1">
<tr><th>00</th><th>01</th><th>02</th><th>03</th><th>04</th><th>05</th><th>06</th><th>07</th><th>08</th><th>09</th><th>10</th><th>11</th><th>12</th><th>13</th><th>14</th><th>15</th><th>16</th><th>17</th><th>18</th><th>19</th><th>20</th><th>21</th><th>22</th><th>23</th><th>24</th><th>25</th><th>26</th><th>27</th><th>28</th><th>29</th><th>30</th><th>31</th></tr>
<tr><td colspan="8">Type</td><td colspan="8">Code</td><td colspan="16">Checksum</td></tr>
<tr><td colspan="32">Message-specific fields and data</td></tr>
</table>

| Field | Size | Description | Example |
| --- | ---: | --- | --- |
| Type | 1 byte | Identifies the ICMP message type | `08` |
| Code | 1 byte | Provides additional context for the message type | `00` |
| Checksum | 2 bytes | Covers the ICMP header and message data | `00 00` |
| Message-specific fields and data | *variable* | Depends on the ICMP message type | `00 01 00 01 68 65 6c 6c 6f` |

```text
08 00 00 00 00 01 00 01 68 65 6c 6c 6f
```

## 7. Various Notes

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